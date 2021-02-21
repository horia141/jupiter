"""The service for dealing with metrics."""
import logging
from dataclasses import dataclass
from typing import Optional, Final, Iterable

from models.basic import EntityId, MetricKey, RecurringTaskPeriod, BasicValidator, SyncPrefer, MetricUnit, \
    ADate, EntityName
from remote.notion.common import NotionPageLink, CollectionEntityNotFound
from remote.notion.metrics_manager import NotionMetricManager
from repository.metrics import YamlMetricsRepository, YamlMetricEntryRepository, MetricEntryRow, MetricRow
from service.errors import ServiceError
from utils.storage import StructuredStorageError
from utils.time_field_action import TimeFieldAction

LOGGER = logging.getLogger(__name__)


@dataclass()
class Metric:
    """A metrics."""
    ref_id: EntityId
    key: MetricKey
    name: str
    archived: bool
    collection_period: Optional[RecurringTaskPeriod]
    metric_unit: Optional[MetricUnit]


@dataclass()
class MetricEntry:
    """A metric entry."""
    ref_id: EntityId
    metric_ref_id: EntityId
    collection_time: ADate
    value: float
    notes: Optional[str]
    archived: bool


class MetricsService:
    """The service class for dealing with metrics."""

    _basic_validator: Final[BasicValidator]
    _metrics_repository: Final[YamlMetricsRepository]
    _metric_entries_repository: Final[YamlMetricEntryRepository]
    _notion_manager: Final[NotionMetricManager]

    def __init__(
            self, basic_validator: BasicValidator, metrics_repository: YamlMetricsRepository,
            metric_entries_repository: YamlMetricEntryRepository, notion_manager: NotionMetricManager) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._metrics_repository = metrics_repository
        self._metric_entries_repository = metric_entries_repository
        self._notion_manager = notion_manager

    def upsert_root_notion_structure(self, parent_page: NotionPageLink) -> None:
        """Create the root page where all the metrics will be linked to."""
        self._notion_manager.upsert_root_page(parent_page)

    def upsert_metric_structure(self, ref_id: EntityId) -> None:
        """Upsert the structure around the metric."""
        metric_row = self._metrics_repository.load_metric(ref_id)
        self._notion_manager.upsert_metric_collection(metric_row.ref_id, metric_row.name)

    def load_all_metrics(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[MetricKey]] = None) -> Iterable[Metric]:
        """Retrieve all the metrics."""
        metric_rows = self._metrics_repository.find_all_old(
            allow_archived=allow_archived, filter_ref_ids=filter_ref_ids, filter_keys=filter_keys)

        return [self._metric_row_to_entity(m) for m in metric_rows]

    def hard_remove_metric(self, ref_id: EntityId) -> Metric:
        """Hard remove a metric."""
        metric_row = self._metrics_repository.remove_metric(ref_id)

        for metric_entry in self._metric_entries_repository.find_all_metric_entries(
                filter_metric_ref_ids=[metric_row.ref_id]):
            self._metric_entries_repository.remove_metric_entry(metric_entry.ref_id)

        LOGGER.info("Applied local changes")

        try:
            self._notion_manager.hard_remove_metric_collection(ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because metric was not found")

        return self._metric_row_to_entity(metric_row)

    def remove_metric_on_notion_side(self, ref_id: EntityId) -> Metric:
        """Remove collection for a metric on Notion-side."""
        metric_row = self._metrics_repository.load_metric(ref_id, allow_archived=True)

        try:
            self._notion_manager.hard_remove_metric_collection(ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because metric was not found")

        return self._metric_row_to_entity(metric_row)

    def load_all_metric_entries(
            self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_metric_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[MetricEntry]:
        """Find all the metric entries."""
        metric_entry_rows = self._metric_entries_repository.find_all_metric_entries(
            allow_archived=allow_archived, filter_ref_ids=filter_ref_ids, filter_metric_ref_ids=filter_metric_ref_ids)
        return [self._metric_entry_row_to_entity(me)
                for me in metric_entry_rows]

    def load_all_metric_entries_not_notion_gced(self, metric_ref_id: EntityId) -> Iterable[MetricEntry]:
        """Retrieve all metric entries which haven't been gced on Notion side."""
        allowed_ref_ids = set(self._notion_manager.load_all_saved_metric_entries_ref_ids(metric_ref_id))
        metric_entry_rows = self._metric_entries_repository.find_all_metric_entries(
            allow_archived=True, filter_metric_ref_ids=[metric_ref_id])
        return [self._metric_entry_row_to_entity(me)
                for me in metric_entry_rows
                if me.ref_id in allowed_ref_ids]

    def hard_remove_metric_entry(self, ref_id: EntityId) -> MetricEntry:
        """Hard remove a metric entry."""
        metric_entry_row = self._metric_entries_repository.remove_metric_entry(ref_id)
        LOGGER.info("Applied local changes")

        try:
            self._notion_manager.hard_remove_metric_entry(
                metric_entry_row.metric_ref_id, metric_entry_row.ref_id)
            LOGGER.info("Applied Notion changes")
        except StructuredStorageError:
            LOGGER.info("Skipping har removal on Notion side because recurring task was not found")

        return self._metric_entry_row_to_entity(metric_entry_row)

    def remove_metric_entry_on_notion_side(self, ref_id: EntityId) -> MetricEntry:
        """Remove entry for a metric on Notion-side."""
        metric_entry_row = self._metric_entries_repository.load_metric_entry(ref_id, allow_archived=True)
        LOGGER.info("Applied local changes")

        try:
            self._notion_manager.hard_remove_metric_entry(
                metric_entry_row.metric_ref_id, metric_entry_row.ref_id)
            LOGGER.info("Applied Notion changes")
        except StructuredStorageError:
            LOGGER.info("Skipping har removal on Notion side because recurring task was not found")

        return self._metric_entry_row_to_entity(metric_entry_row)

    def sync_metric_and_metric_entries(
            self, metric_ref_id: EntityId, drop_all_notion_side: bool, sync_even_if_not_modified: bool,
            filter_metric_entry_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> Iterable[MetricEntry]:
        """Synchronize a metric and its entries between Notion and local storage."""
        # Synchronize the metric.
        metric_row = self._metrics_repository.load_metric(metric_ref_id)

        try:
            metric_notion_collection = self._notion_manager.load_metric_collection(metric_ref_id)

            if sync_prefer == SyncPrefer.LOCAL:
                metric_notion_collection.name = metric_row.name
                self._notion_manager.save_metric_collection(metric_notion_collection)
                LOGGER.info("Applied changes to Notion")
            elif sync_prefer == SyncPrefer.NOTION:
                metric_row.name = EntityName(metric_notion_collection.name)
                self._metrics_repository.update_metric(metric_row)
                LOGGER.info("Applied local change")
            else:
                raise Exception(f"Invalid preference {sync_prefer}")
        except StructuredStorageError:
            LOGGER.info("Trying to recreate the metric")
            self._notion_manager.upsert_metric_collection(metric_ref_id, metric_row.name)

        # Now synchronize the list items here.
        filter_metric_entry_ref_ids_set = frozenset(filter_metric_entry_ref_ids) \
            if filter_metric_entry_ref_ids else None

        all_metric_entries_rows = self._metric_entries_repository.find_all_metric_entries(
            allow_archived=True, filter_metric_ref_ids=[metric_ref_id],
            filter_ref_ids=filter_metric_entry_ref_ids)
        all_metric_entries_rows_set = {sli.ref_id: sli for sli in all_metric_entries_rows}

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
            if filter_metric_entry_ref_ids_set is not None and \
                    metric_entry_notion_row.ref_id not in filter_metric_entry_ref_ids_set:
                LOGGER.info(
                    f"Skipping '{metric_entry_notion_row.collection_time}' (id={metric_entry_notion_row.notion_id})")
                continue

            LOGGER.info(f"Syncing '{metric_entry_notion_row.collection_time}' (id={metric_entry_notion_row.notion_id})")

            if metric_entry_notion_row.ref_id is None or metric_entry_notion_row.ref_id == "":
                # If the metric entry doesn't exist locally, we create it.
                new_metric_entry_row = self._metric_entries_repository.create_metric_entry(
                    metric_ref_id=metric_ref_id,
                    collection_time=metric_entry_notion_row.collection_time,
                    value=metric_entry_notion_row.value,
                    notes=metric_entry_notion_row.notes,
                    archived=metric_entry_notion_row.archived)
                LOGGER.info(f"Found new metric entry from Notion '{new_metric_entry_row.collection_time}'")

                self._notion_manager.link_local_and_notion_entries_for_metric(
                    metric_ref_id, new_metric_entry_row.ref_id, metric_entry_notion_row.notion_id)
                LOGGER.info(f"Linked the new metric entry with local entries")

                metric_entry_notion_row.ref_id = new_metric_entry_row.ref_id
                self._notion_manager.save_metric_entry(
                    metric_ref_id, new_metric_entry_row.ref_id, metric_entry_notion_row)
                LOGGER.info(f"Applied changes on Notion side too")

                metric_entries_notion_rows_set[EntityId(metric_entry_notion_row.ref_id)] = \
                    metric_entry_notion_row
            elif metric_entry_notion_row.ref_id in all_metric_entries_rows_set and \
                    metric_entry_notion_row.notion_id in all_metric_entries_notion_ids:
                metric_entry_row = all_metric_entries_rows_set[EntityId(metric_entry_notion_row.ref_id)]
                metric_entries_notion_rows_set[EntityId(metric_entry_notion_row.ref_id)] = \
                    metric_entry_notion_row

                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified and \
                            metric_entry_notion_row.last_edited_time <= metric_entry_row.last_modified_time:
                        LOGGER.info(f"Skipping '{metric_entry_notion_row.collection_time}' because it was not modified")
                        continue

                    archived_time_action = \
                        TimeFieldAction.SET if not metric_entry_row.archived \
                                               and metric_entry_notion_row.archived else \
                            TimeFieldAction.CLEAR if metric_entry_row.archived \
                                                     and not metric_entry_notion_row.archived else \
                                TimeFieldAction.DO_NOTHING
                    metric_entry_row.collection_time = metric_entry_notion_row.collection_time
                    metric_entry_row.value = metric_entry_notion_row.value
                    metric_entry_row.notes = metric_entry_notion_row.notes
                    metric_entry_row.archived = metric_entry_notion_row.archived
                    self._metric_entries_repository.update_metric_entry(metric_entry_row, archived_time_action)
                    LOGGER.info(f"Changed metric entry '{metric_entry_row.collection_time}' from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified and \
                            metric_entry_row.last_modified_time <= metric_entry_notion_row.last_edited_time:
                        LOGGER.info(f"Skipping '{metric_entry_notion_row.collection_time}' because it was not modified")
                        continue

                    metric_entry_notion_row.collection_time = metric_entry_row.collection_time
                    metric_entry_notion_row.value = metric_entry_row.value
                    metric_entry_notion_row.notes = metric_entry_row.notes
                    metric_entry_notion_row.archived = metric_entry_row.archived
                    self._notion_manager.save_metric_entry(
                        metric_ref_id, metric_entry_row.ref_id, metric_entry_notion_row)
                    LOGGER.info(f"Changed metric entry '{metric_entry_notion_row.collection_time}' from local")
                else:
                    raise ServiceError(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random metric entry added by someone, where they completed themselves a ref_id.
                #    It's a bad setup, and we remove it.
                # 2. This is a metric entry added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                self._notion_manager.hard_remove_metric_entry(
                    metric_ref_id, EntityId(metric_entry_notion_row.ref_id))
                LOGGER.info(f"Removed metric entry with id={metric_entry_notion_row.ref_id} from Notion")

        for metric_entry_row in all_metric_entries_rows:
            if metric_entry_row.ref_id in metric_entries_notion_rows_set:
                # The metric entry already exists on Notion side, so it was handled by the above loop!
                continue
            if metric_entry_row.archived:
                continue

            # If the metric entry does not exist on Notion side, we create it.
            self._notion_manager.upsert_metric_entry_old(
                metric_ref_id=metric_ref_id,
                ref_id=metric_entry_row.ref_id,
                collection_time=metric_entry_row.collection_time,
                value=metric_entry_row.value,
                notes=metric_entry_row.notes,
                archived=metric_entry_row.archived)
            LOGGER.info(f"Created new metric entry on Notion side '{metric_entry_row.collection_time}'")

        return [self._metric_entry_row_to_entity(me)
                for me in all_metric_entries_rows_set.values()]

    @staticmethod
    def _metric_row_to_entity(row: MetricRow) -> Metric:
        return Metric(
            ref_id=row.ref_id,
            key=row.key,
            name=row.name,
            archived=row.archived,
            collection_period=row.collection_period,
            metric_unit=row.metric_unit)

    @staticmethod
    def _metric_entry_row_to_entity(row: MetricEntryRow) -> MetricEntry:
        return MetricEntry(
            ref_id=row.ref_id,
            metric_ref_id=row.metric_ref_id,
            collection_time=row.collection_time,
            value=row.value,
            notes=row.notes,
            archived=row.archived)
