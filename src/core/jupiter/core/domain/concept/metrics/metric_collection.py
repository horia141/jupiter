"""A metric collection."""

from jupiter.core.domain.concept.metrics.metric import Metric
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    IsRefId,
    ParentLink,
    TrunkEntity,
    create_entity_action,
    entity,
    update_entity_action,
)


@entity
class MetricCollection(TrunkEntity):
    """A metric collection."""

    workspace: ParentLink
    collection_project_ref_id: EntityId

    metrics = ContainsMany(Metric, metric_collection_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_metric_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
        collection_project_ref_id: EntityId,
    ) -> "MetricCollection":
        """Create a metric collection."""
        return MetricCollection._create(
            ctx,
            workspace=ParentLink(workspace_ref_id),
            collection_project_ref_id=collection_project_ref_id,
        )

    @update_entity_action
    def change_collection_project(
        self,
        ctx: DomainContext,
        collection_project_ref_id: EntityId,
    ) -> "MetricCollection":
        """Change the catch up project."""
        return self._new_version(
            ctx,
            collection_project_ref_id=collection_project_ref_id,
        )
