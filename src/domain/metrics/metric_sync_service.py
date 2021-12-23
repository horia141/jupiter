"""The service class for syncing the METRIC database between local and Notion."""
import logging
from typing import Final, Iterable, Dict, Optional

from domain.errors import ServiceError
from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from domain.metrics.metric import Metric
from domain.metrics.metric_entry import MetricEntry
from domain.metrics.notion_metric_entry import NotionMetricEntry
from domain.sync_prefer import SyncPrefer
from framework.base.timestamp import Timestamp
from framework.base.entity_id import EntityId
from utils.storage import StructuredStorageError

LOGGER = logging.getLogger(__name__)


class MetricSyncService:
    """The service class for syncing the METRIC database between local and Notion."""

    _metric_engine: Final[MetricEngine]
    _metric_notion_manager: Final[MetricNotionManager]

    def __init__(
            self, metric_engine: MetricEngine, metric_notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._metric_engine = metric_engine
        self._metric_notion_manager = metric_notion_manager

    def sync(
            self, right_now: Timestamp, metric: Metric, drop_all_notion_side: bool, sync_even_if_not_modified: bool,
            filter_metric_entry_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> Iterable[MetricEntry]:
        """Synchronize a metric and its entries between Notion and local storage."""
        try:
            notion_metric = self._metric_notion_manager.load_metric(metric)

            if sync_prefer == SyncPrefer.LOCAL:
                updated_notion_metric = notion_metric.join_with_aggregate_root(metric)
                self._metric_notion_manager.save_metric(updated_notion_metric)
                LOGGER.info("Applied changes to Notion")
            elif sync_prefer == SyncPrefer.NOTION:
                updated_metric = notion_metric.apply_to_aggregate_root(metric, right_now)
                with self._metric_engine.get_unit_of_work() as uow:
                    uow.metric_repository.save(updated_metric)
                LOGGER.info("Applied local change")
            else:
                raise Exception(f"Invalid preference {sync_prefer}")
        except StructuredStorageError:
            LOGGER.info("Trying to recreate the metric")
            self._metric_notion_manager.upsert_metric(metric)

        # Now synchronize the list items here.
        filter_metric_entry_ref_ids_set = frozenset(filter_metric_entry_ref_ids) \
            if filter_metric_entry_ref_ids else None

        with self._metric_engine.get_unit_of_work() as uow:
            all_metric_entries = uow.metric_entry_repository.find_all(
                allow_archived=True, filter_metric_ref_ids=[metric.ref_id],
                filter_ref_ids=filter_metric_entry_ref_ids)
        all_metric_entries_set: Dict[EntityId, MetricEntry] = {sli.ref_id: sli for sli in all_metric_entries}

        if not drop_all_notion_side:
            all_notion_metric_entries = \
                self._metric_notion_manager.load_all_metric_entries(metric)
            all_notion_metric_notion_ids = \
                set(self._metric_notion_manager.load_all_saved_metric_entries_notion_ids(metric))
        else:
            self._metric_notion_manager.drop_all_metric_entries(metric)
            all_notion_metric_entries = []
            all_notion_metric_notion_ids = set()
        notion_metric_entries_set = {}

        # Explore Notion and apply to local
        for notion_metric_entry in all_notion_metric_entries:
            notion_metric_ref_id = EntityId.from_raw(notion_metric_entry.ref_id) \
                if notion_metric_entry.ref_id else None
            if filter_metric_entry_ref_ids_set is not None and \
                    notion_metric_ref_id not in filter_metric_entry_ref_ids_set:
                LOGGER.info(
                    f"Skipping '{notion_metric_entry.collection_time}' (id={notion_metric_entry.notion_id})")
                continue

            LOGGER.info(f"Syncing '{notion_metric_entry.collection_time}' (id={notion_metric_entry.notion_id})")

            if notion_metric_ref_id is None or notion_metric_entry.ref_id == "":
                # If the metric entry doesn't exist locally, we create it.
                new_metric_entry = \
                    notion_metric_entry.new_aggregate_root(NotionMetricEntry.InverseExtraInfo(metric.ref_id))
                with self._metric_engine.get_unit_of_work() as uow:
                    new_metric_entry = uow.metric_entry_repository.create(new_metric_entry)
                LOGGER.info(f"Found new metric entry from Notion '{new_metric_entry.collection_time}'")

                self._metric_notion_manager.link_local_and_notion_entries_for_metric(
                    metric.ref_id, new_metric_entry.ref_id, notion_metric_entry.notion_id)
                LOGGER.info(f"Linked the new metric entry with local entries")

                notion_metric_entry = notion_metric_entry.join_with_aggregate_root(new_metric_entry, None)
                self._metric_notion_manager.save_metric_entry(metric, notion_metric_entry)
                LOGGER.info(f"Applied changes on Notion side too")

                notion_metric_entries_set[new_metric_entry.ref_id] = notion_metric_entry
            elif notion_metric_ref_id in all_metric_entries_set and \
                    notion_metric_entry.notion_id in all_notion_metric_notion_ids:
                metric_entry = all_metric_entries_set[notion_metric_ref_id]
                notion_metric_entries_set[notion_metric_ref_id] = notion_metric_entry

                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified and \
                            notion_metric_entry.last_edited_time <= metric_entry.last_modified_time:
                        LOGGER.info(f"Skipping '{notion_metric_entry.collection_time}' because it was not modified")
                        continue

                    updated_metric_entry = \
                        notion_metric_entry.apply_to_aggregate_root(
                            metric_entry, NotionMetricEntry.InverseExtraInfo(metric.ref_id))

                    with self._metric_engine.get_unit_of_work() as uow:
                        uow.metric_entry_repository.save(updated_metric_entry)
                    LOGGER.info(f"Changed metric entry '{metric_entry.collection_time}' from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified and \
                            metric_entry.last_modified_time <= notion_metric_entry.last_edited_time:
                        LOGGER.info(f"Skipping '{notion_metric_entry.collection_time}' because it was not modified")
                        continue

                    updated_notion_metric_entry = notion_metric_entry.join_with_aggregate_root(metric_entry, None)
                    self._metric_notion_manager.save_metric_entry(metric, updated_notion_metric_entry)
                    LOGGER.info(f"Changed metric entry '{notion_metric_entry.collection_time}' from local")
                else:
                    raise ServiceError(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random metric entry added by someone, where they completed themselves a ref_id.
                #    It's a bad setup, and we remove it.
                # 2. This is a metric entry added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                self._metric_notion_manager.remove_metric_entry(
                    metric.ref_id,
                    EntityId.from_raw(notion_metric_entry.ref_id) if notion_metric_entry.ref_id else None)
                LOGGER.info(f"Removed metric entry with id={notion_metric_entry.ref_id} from Notion")

        for metric_entry in all_metric_entries:
            if metric_entry.ref_id in notion_metric_entries_set:
                # The metric entry already exists on Notion side, so it was handled by the above loop!
                continue
            if metric_entry.archived:
                continue

            # If the metric entry does not exist on Notion side, we create it.
            self._metric_notion_manager.upsert_metric_entry(metric_entry)
            LOGGER.info(f"Created new metric entry on Notion side '{metric_entry.collection_time}'")

        return list(all_metric_entries_set.values())
