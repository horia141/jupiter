"""The service for dealing with metrics."""
import logging
from typing import Optional, Final, Iterable, List, Dict

from domain.common.entity_name import EntityName
from domain.common.sync_prefer import SyncPrefer
from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.metric import Metric
from domain.metrics.metric_entry import MetricEntry
from domain.metrics.metric_key import MetricKey
from models.framework import EntityId
from remote.notion.common import NotionPageLink, CollectionEntityNotFound
from remote.notion.metrics_manager import NotionMetricManager
from service.errors import ServiceError
from utils.storage import StructuredStorageError
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MetricsService:
    """The service class for dealing with metrics."""

    _time_provider: Final[TimeProvider]
    _metric_engine: Final[MetricEngine]
    _notion_manager: Final[NotionMetricManager]

    def __init__(
            self, time_provider: TimeProvider, metric_engine: MetricEngine,
            notion_manager: NotionMetricManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._metric_engine = metric_engine
        self._notion_manager = notion_manager

    def upsert_root_notion_structure(self, parent_page: NotionPageLink) -> None:
        """Create the root page where all the metrics will be linked to."""
        self._notion_manager.upsert_root_page(parent_page)

    def upsert_metric_structure(self, ref_id: EntityId) -> None:
        """Upsert the structure around the metric."""
        with self._metric_engine.get_unit_of_work() as uow:
            metric_row = uow.metric_repository.get_by_id(ref_id, allow_archived=False)
        self._notion_manager.upsert_metric_collection(metric_row.ref_id, metric_row.name)

    def load_all_metrics(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[MetricKey]] = None) -> List[Metric]:
        """Retrieve all the metrics."""
        with self._metric_engine.get_unit_of_work() as uow:
            return uow.metric_repository.find_all(
                allow_archived=allow_archived, filter_ref_ids=filter_ref_ids, filter_keys=filter_keys)

    def hard_remove_metric(self, ref_id: EntityId) -> None:
        """Hard remove a metric."""
        with self._metric_engine.get_unit_of_work() as uow:
            uow.metric_repository.remove(ref_id)

            for metric_entry in uow.metric_entry_repository.find_all(filter_metric_ref_ids=[ref_id]):
                uow.metric_entry_repository.remove(metric_entry.ref_id)

            LOGGER.info("Applied local changes")

        try:
            self._notion_manager.hard_remove_metric_collection(ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because metric was not found")

    def remove_metric_on_notion_side(self, ref_id: EntityId) -> Metric:
        """Remove collection for a metric on Notion-side."""
        with self._metric_engine.get_unit_of_work() as uow:
            metric = uow.metric_repository.get_by_id(ref_id, allow_archived=True)

        try:
            self._notion_manager.hard_remove_metric_collection(ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because metric was not found")

        return metric

    def load_all_metric_entries(
            self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_metric_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[MetricEntry]:
        """Find all the metric entries."""
        with self._metric_engine.get_unit_of_work() as uow:
            return uow.metric_entry_repository.find_all(
                allow_archived=allow_archived, filter_ref_ids=filter_ref_ids,
                filter_metric_ref_ids=filter_metric_ref_ids)

    def load_all_metric_entries_not_notion_gced(self, metric_ref_id: EntityId) -> Iterable[MetricEntry]:
        """Retrieve all metric entries which haven't been gced on Notion side."""
        allowed_ref_ids = set(self._notion_manager.load_all_saved_metric_entries_ref_ids(metric_ref_id))
        with self._metric_engine.get_unit_of_work() as uow:
            return uow.metric_entry_repository.find_all(
                allow_archived=True, filter_ref_ids=allowed_ref_ids, filter_metric_ref_ids=[metric_ref_id])

    def hard_remove_metric_entry(self, ref_id: EntityId) -> None:
        """Hard remove a metric entry."""
        with self._metric_engine.get_unit_of_work() as uow:
            metric_entry = uow.metric_entry_repository.remove(ref_id)
            LOGGER.info("Applied local changes")

        try:
            self._notion_manager.hard_remove_metric_entry(
                metric_entry.metric_ref_id, ref_id)
            LOGGER.info("Applied Notion changes")
        except StructuredStorageError:
            LOGGER.info("Skipping har removal on Notion side because recurring task was not found")

    def remove_metric_entry_on_notion_side(self, ref_id: EntityId) -> None:
        """Remove entry for a metric on Notion-side."""
        with self._metric_engine.get_unit_of_work() as uow:
            metric_entry = uow.metric_entry_repository.load_by_id(ref_id, allow_archived=True)

        try:
            self._notion_manager.hard_remove_metric_entry(
                metric_entry.metric_ref_id, metric_entry.ref_id)
            LOGGER.info("Applied Notion changes")
        except StructuredStorageError:
            LOGGER.info("Skipping har removal on Notion side because recurring task was not found")

    def sync_metric_and_metric_entries(
            self, metric_ref_id: EntityId, drop_all_notion_side: bool, sync_even_if_not_modified: bool,
            filter_metric_entry_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> Iterable[MetricEntry]:
        """Synchronize a metric and its entries between Notion and local storage."""
        # Synchronize the metric.
        with self._metric_engine.get_unit_of_work() as uow:
            metric = uow.metric_repository.get_by_id(metric_ref_id, allow_archived=False)

        try:
            metric_notion_collection = self._notion_manager.load_metric_collection(metric_ref_id)

            if sync_prefer == SyncPrefer.LOCAL:
                metric_notion_collection.name = str(metric.name)
                self._notion_manager.save_metric_collection(metric_notion_collection)
                LOGGER.info("Applied changes to Notion")
            elif sync_prefer == SyncPrefer.NOTION:
                metric.change_name(EntityName(metric_notion_collection.name), self._time_provider.get_current_time())
                with self._metric_engine.get_unit_of_work() as uow:
                    uow.metric_repository.save(metric)
                LOGGER.info("Applied local change")
            else:
                raise Exception(f"Invalid preference {sync_prefer}")
        except StructuredStorageError:
            LOGGER.info("Trying to recreate the metric")
            self._notion_manager.upsert_metric_collection(metric_ref_id, metric.name)

        # Now synchronize the list items here.
        filter_metric_entry_ref_ids_set = frozenset(filter_metric_entry_ref_ids) \
            if filter_metric_entry_ref_ids else None

        with self._metric_engine.get_unit_of_work() as uow:
            all_metric_entries = uow.metric_entry_repository.find_all(
                allow_archived=True, filter_metric_ref_ids=[metric_ref_id],
                filter_ref_ids=filter_metric_entry_ref_ids)
        all_metric_entries_set: Dict[EntityId, MetricEntry] = {sli.ref_id: sli for sli in all_metric_entries}

        if not drop_all_notion_side:
            all_metric_entries_notion_rows = \
                self._notion_manager.load_all_metric_entries(metric_ref_id)
            all_metric_entries_notion_ids = \
                set(self._notion_manager.load_all_saved_metric_entries_notion_ids(metric_ref_id))
        else:
            self._notion_manager.drop_all_metric_entries(metric_ref_id)
            all_metric_entries_notion_rows = []
            all_metric_entries_notion_ids = set()
        metric_entries_notion_rows_set = {}

        # Explore Notion and apply to local
        for metric_entry_notion_row in all_metric_entries_notion_rows:
            notion_metric_ref_id = EntityId.from_raw(metric_entry_notion_row.ref_id) \
                if metric_entry_notion_row.ref_id else None
            if filter_metric_entry_ref_ids_set is not None and \
                    notion_metric_ref_id not in filter_metric_entry_ref_ids_set:
                LOGGER.info(
                    f"Skipping '{metric_entry_notion_row.collection_time}' (id={metric_entry_notion_row.notion_id})")
                continue

            LOGGER.info(f"Syncing '{metric_entry_notion_row.collection_time}' (id={metric_entry_notion_row.notion_id})")

            if notion_metric_ref_id is None or metric_entry_notion_row.ref_id == "":
                # If the metric entry doesn't exist locally, we create it.
                new_metric_entry = MetricEntry.new_metric_entry(
                    archived=metric_entry_notion_row.archived,
                    metric_ref_id=metric_ref_id,
                    collection_time=metric_entry_notion_row.collection_time,
                    value=metric_entry_notion_row.value,
                    notes=metric_entry_notion_row.notes,
                    created_time=metric_entry_notion_row.last_edited_time)
                with self._metric_engine.get_unit_of_work() as uow:
                    new_metric_entry = uow.metric_entry_repository.create(new_metric_entry)
                LOGGER.info(f"Found new metric entry from Notion '{new_metric_entry.collection_time}'")

                self._notion_manager.link_local_and_notion_entries_for_metric(
                    metric_ref_id, new_metric_entry.ref_id, metric_entry_notion_row.notion_id)
                LOGGER.info(f"Linked the new metric entry with local entries")

                metric_entry_notion_row.ref_id = str(new_metric_entry.ref_id)
                self._notion_manager.save_metric_entry(
                    metric_ref_id, new_metric_entry.ref_id, metric_entry_notion_row)
                LOGGER.info(f"Applied changes on Notion side too")

                metric_entries_notion_rows_set[new_metric_entry.ref_id] = metric_entry_notion_row
            elif notion_metric_ref_id in all_metric_entries_set and \
                    metric_entry_notion_row.notion_id in all_metric_entries_notion_ids:
                metric_entry = all_metric_entries_set[notion_metric_ref_id]
                metric_entries_notion_rows_set[notion_metric_ref_id] = metric_entry_notion_row

                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified and \
                            metric_entry_notion_row.last_edited_time <= metric_entry.last_modified_time:
                        LOGGER.info(f"Skipping '{metric_entry_notion_row.collection_time}' because it was not modified")
                        continue

                    metric_entry.change_collection_time(
                        metric_entry_notion_row.collection_time, metric_entry_notion_row.last_edited_time)
                    metric_entry.change_value(metric_entry_notion_row.value, metric_entry_notion_row.last_edited_time)
                    metric_entry.change_notes(metric_entry_notion_row.notes, metric_entry_notion_row.last_edited_time)
                    metric_entry.change_archived(
                        metric_entry_notion_row.archived, metric_entry_notion_row.last_edited_time)
                    with self._metric_engine.get_unit_of_work() as uow:
                        uow.metric_entry_repository.save(metric_entry)
                    LOGGER.info(f"Changed metric entry '{metric_entry.collection_time}' from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified and \
                            metric_entry.last_modified_time <= metric_entry_notion_row.last_edited_time:
                        LOGGER.info(f"Skipping '{metric_entry_notion_row.collection_time}' because it was not modified")
                        continue

                    metric_entry_notion_row.collection_time = metric_entry.collection_time
                    metric_entry_notion_row.value = metric_entry.value
                    metric_entry_notion_row.notes = metric_entry.notes
                    metric_entry_notion_row.archived = metric_entry.archived
                    self._notion_manager.save_metric_entry(
                        metric_ref_id, metric_entry.ref_id, metric_entry_notion_row)
                    LOGGER.info(f"Changed metric entry '{metric_entry_notion_row.collection_time}' from local")
                else:
                    raise ServiceError(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random metric entry added by someone, where they completed themselves a ref_id.
                #    It's a bad setup, and we remove it.
                # 2. This is a metric entry added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                self._notion_manager.hard_remove_metric_entry(metric_ref_id, notion_metric_ref_id)
                LOGGER.info(f"Removed metric entry with id={metric_entry_notion_row.ref_id} from Notion")

        for metric_entry in all_metric_entries:
            if metric_entry.ref_id in metric_entries_notion_rows_set:
                # The metric entry already exists on Notion side, so it was handled by the above loop!
                continue
            if metric_entry.archived:
                continue

            # If the metric entry does not exist on Notion side, we create it.
            self._notion_manager.upsert_metric_entry_old(
                metric_ref_id=metric_ref_id,
                ref_id=metric_entry.ref_id,
                collection_time=metric_entry.collection_time,
                value=metric_entry.value,
                notes=metric_entry.notes,
                archived=metric_entry.archived)
            LOGGER.info(f"Created new metric entry on Notion side '{metric_entry.collection_time}'")

        return list(all_metric_entries_set.values())
