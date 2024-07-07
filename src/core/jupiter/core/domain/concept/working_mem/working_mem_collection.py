"""The working memory log."""
from jupiter.core.domain.concept.working_mem.working_mem import WorkingMem
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
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
from jupiter.core.framework.errors import InputValidationError


@entity
class WorkingMemCollection(TrunkEntity):
    """The working memory log."""

    workspace: ParentLink

    generation_period: RecurringTaskPeriod
    cleanup_project_ref_id: EntityId

    working_mems = ContainsMany(WorkingMem, working_mem_collection_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_working_mem_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
        generation_period: RecurringTaskPeriod,
        cleanup_project_ref_id: EntityId,
    ) -> "WorkingMemCollection":
        """Create a new working memory log."""
        if (
            generation_period != RecurringTaskPeriod.DAILY
            and generation_period != RecurringTaskPeriod.WEEKLY
        ):
            raise InputValidationError(f"Invalid period: {generation_period}")
        return WorkingMemCollection._create(
            ctx,
            workspace=ParentLink(workspace_ref_id),
            generation_period=generation_period,
            cleanup_project_ref_id=cleanup_project_ref_id,
        )

    @update_entity_action
    def change_generation_period(
        self,
        ctx: DomainContext,
        generation_period: RecurringTaskPeriod,
    ) -> "WorkingMemCollection":
        """Change the generation period."""
        if (
            generation_period != RecurringTaskPeriod.DAILY
            and generation_period != RecurringTaskPeriod.WEEKLY
        ):
            raise InputValidationError(f"Invalid period: {generation_period}")
        return self._new_version(
            ctx,
            generation_period=generation_period,
        )

    @update_entity_action
    def change_cleanup_project(
        self,
        ctx: DomainContext,
        cleanup_project_ref_id: EntityId,
    ) -> "WorkingMemCollection":
        """Change the cleanup project."""
        return self._new_version(
            ctx,
            cleanup_project_ref_id=cleanup_project_ref_id,
        )
