"""The controller for metrics."""
from dataclasses import dataclass
from typing import Final, Optional, Iterable

from controllers.common import ControllerInputValidationError
from models.basic import MetricKey, MetricUnit, RecurringTaskPeriod, EntityId, ADate
from service.metrics import MetricsService, Metric, MetricEntry
from utils.time_provider import TimeProvider


@dataclass()
class LoadAllMetricsEntry:
    """A single entry in the LoadAllMetricsResponse."""

    metric: Metric
    metric_entries: Iterable[MetricEntry]


@dataclass()
class LoadAllMetricsResponse:
    """Response object for the load_all_metrics controller method."""

    metrics: Iterable[LoadAllMetricsEntry]


@dataclass()
class LoadAllMetricEntriesEntry:
    """A single entry in the LoadAllMetricEntriesResponse."""

    metric_entry: MetricEntry
    metric: Metric


@dataclass()
class LoadAllMetricEntriesResponse:
    """Response object for the load_all_metric_entries controller method."""

    metric_entries: Iterable[LoadAllMetricEntriesEntry]


class MetricsController:
    """The controller for metrics."""

    _time_provider: Final[TimeProvider]
    _metrics_service: Final[MetricsService]

    def __init__(self, time_provider: TimeProvider, metrics_service: MetricsService) -> None:
        """Controller."""
        self._time_provider = time_provider
        self._metrics_service = metrics_service

    def create_metric(self, key: MetricKey, name: str, collection_period: Optional[RecurringTaskPeriod],
                      metric_unit: Optional[MetricUnit]) -> Metric:
        """Create a new metric."""
        return self._metrics_service.create_metric(key, name, collection_period, metric_unit)

    def archive_metric(self, key: MetricKey) -> Metric:
        """Archive metric."""
        metric = self._metrics_service.load_metric_by_key(key)
        return self._metrics_service.archive_metric(metric.ref_id)

    def set_metric_name(self, key: MetricKey, name: str) -> Metric:
        """Change metric name."""
        metric = self._metrics_service.load_metric_by_key(key)
        return self._metrics_service.set_metric_name(metric.ref_id, name)

    def set_metric_collection_period(
            self, key: MetricKey, collection_period: Optional[RecurringTaskPeriod]) -> Metric:
        """Change metric collection period."""
        metric = self._metrics_service.load_metric_by_key(key)
        return self._metrics_service.set_metric_collection_period(metric.ref_id, collection_period)

    def load_all_metrics(
            self, allow_archived: bool = False,
            filter_keys: Optional[Iterable[MetricKey]] = None) -> LoadAllMetricsResponse:
        """Load all metrics."""
        metrics = self._metrics_service.load_all_metrics(
            allow_archived=allow_archived, filter_keys=filter_keys)
        metric_entries = self._metrics_service.load_all_metric_entries(
            allow_archived=allow_archived, filter_metric_ref_ids=[m.ref_id for m in metrics])
        metrics_by_ref_ids = {}
        for metric_entry in metric_entries:
            if metric_entry.metric_ref_id not in metrics_by_ref_ids:
                metrics_by_ref_ids[metric_entry.metric_ref_id] = [metric_entry]
            else:
                metrics_by_ref_ids[metric_entry.metric_ref_id].append(metric_entry)
        return LoadAllMetricsResponse(
            metrics=[LoadAllMetricsEntry(
                metric=m,
                metric_entries=metrics_by_ref_ids.get(m.ref_id, [])) for m in metrics])

    def hard_remove_metric(self, keys: Iterable[MetricKey]) -> None:
        """Hard remove metric item."""
        keys = list(keys)
        if len(keys) == 0:
            raise ControllerInputValidationError("Expected at least one entity to remove")

        for key in keys:
            metric = self._metrics_service.load_metric_by_key(key)
            self._metrics_service.hard_remove_metric(metric.ref_id)

    def create_metric_entry(
            self, metric_key: MetricKey, collection_time: Optional[ADate], value: float,
            notes: Optional[str]) -> MetricEntry:
        """Create a metric entry."""
        metric = self._metrics_service.load_metric_by_key(metric_key)
        collection_time = collection_time or self._time_provider.get_current_date()
        return self._metrics_service.create_metric_entry(metric.ref_id, collection_time, value, notes)

    def archive_metric_entry(self, ref_id: EntityId) -> MetricEntry:
        """Archive a metric entry."""
        return self._metrics_service.archive_metric_entry(ref_id)

    def set_metric_entry_collection_time(self, ref_id: EntityId, collection_time: Optional[ADate],) -> MetricEntry:
        """Change the value of a metric entry."""
        collection_time = collection_time or self._time_provider.get_current_date()
        return self._metrics_service.set_metric_entry_collection_time(ref_id, collection_time)

    def set_metric_entry_value(self, ref_id: EntityId, value: float) -> MetricEntry:
        """Change the value of a metric entry."""
        return self._metrics_service.set_metric_entry_value(ref_id, value)

    def set_metric_entry_notes(self, ref_id: EntityId, notes: Optional[str]) -> MetricEntry:
        """Change the value of a metric entry."""
        return self._metrics_service.set_metric_entry_notes(ref_id, notes)

    def load_all_metric_entries(
            self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_metric_keys: Optional[Iterable[MetricKey]] = None) -> LoadAllMetricEntriesResponse:
        """Retrieve all metric entries."""
        metrics = self._metrics_service.load_all_metrics(
            allow_archived=allow_archived, filter_keys=filter_metric_keys)
        metrics_by_ref_id = {m.ref_id: m for m in metrics}
        metric_entries = self._metrics_service.load_all_metric_entries(
            allow_archived=allow_archived, filter_ref_ids=filter_ref_ids,
            filter_metric_ref_ids=[m.ref_id for m in metrics])

        return LoadAllMetricEntriesResponse(
            metric_entries=[LoadAllMetricEntriesEntry(
                metric_entry=me,
                metric=metrics_by_ref_id[me.metric_ref_id]) for me in metric_entries])

    def hard_remove_metric_entries(self, ref_ids: Iterable[EntityId]) -> None:
        """Hard remove metric entries."""
        ref_ids = list(ref_ids)
        if len(ref_ids) == 0:
            raise ControllerInputValidationError("Expected at least one entity to remove")

        for ref_id in ref_ids:
            self._metrics_service.hard_remove_metric_entry(ref_id)
