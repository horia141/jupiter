"""Use case for creating time plan actitivities for chores."""

from jupiter.core.app import AppCore
from jupiter.core.apps.chores.root import Chore
from jupiter.core.apps.time_plans.root import TimePlan
from jupiter.core.apps.time_plans.sub.activity.feasability import (
    TimePlanActivityFeasability,
)
from jupiter.core.apps.time_plans.sub.activity.kind import (
    TimePlanActivityKind,
)
from jupiter.core.apps.time_plans.sub.activity.root import (
    TimePlanActivity,
    TimePlanAlreadyAssociatedWithTargetError,
)
from jupiter.core.apps.time_plans.use_case.associate_with_habits import (
    dates_in_inclusive_range,
    inbox_task_overlaps_time_plan,
)
from jupiter.core.common.sub.access.access_level import AccessLevel
from jupiter.core.common.sub.inbox_tasks.root import InboxTask
from jupiter.core.config import (
    JupiterLoggedInMutationContext,
)
from jupiter.core.crown_entity_support import (
    JupiterUpdateCrownEntityArgs,
    JupiterUpdateCrownEntityUseCase,
)
from jupiter.core.features import WorkspaceFeature
from jupiter.core.gen.service.gen import GenService
from jupiter.core.named_entity_tag import NamedEntityTag
from jupiter.core.sync_target import SyncTarget
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.entity_link import EntityLink
from jupiter.framework.errors import InputValidationError
from jupiter.framework.progress_reporter.reporter import ProgressReporter
from jupiter.framework.storage.repository import DomainUnitOfWork
from jupiter.framework.use_case import (
    mutation_use_case,
)
from jupiter.framework.use_case_io import (
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)


@use_case_args
class TimePlanAssociateWithChoresArgs(JupiterUpdateCrownEntityArgs):
    """Args."""

    ref_id: EntityId
    chore_ref_ids: list[EntityId]
    kind: TimePlanActivityKind
    feasability: TimePlanActivityFeasability


@use_case_result
class TimePlanAssociateWithChoresResult(UseCaseResultBase):
    """Result."""

    new_time_plan_activities: list[TimePlanActivity]


@mutation_use_case(
    WorkspaceFeature.TIME_PLANS, only_for_component=[AppCore.WEBUI, AppCore.API]
)
class TimePlanAssociateWithChoresUseCase(
    JupiterUpdateCrownEntityUseCase[
        TimePlanAssociateWithChoresArgs, TimePlanAssociateWithChoresResult
    ]
):
    """Use case for creating activities starting from chores."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: JupiterLoggedInMutationContext,
        args: TimePlanAssociateWithChoresArgs,
    ) -> TimePlanAssociateWithChoresResult:
        """Execute the command's actions."""
        if len(args.chore_ref_ids) == 0:
            raise InputValidationError("You must specifiy some chores")

        time_plan = await self.load_entity(
            uow, context.user.ref_id, TimePlan, args.ref_id
        )

        if not time_plan.allows_inbox_tasks:
            raise InputValidationError(
                "Chores can only be added to daily or weekly time plans"
            )

        chores = await self.find_all_generic(
            uow,
            context.user.ref_id,
            Chore,
            allow_archived=False,
            ref_id=args.chore_ref_ids,
            minimum_access_level=AccessLevel.READER,
        )
        chores = [chore for chore in chores if not chore.suspended]

        new_time_plan_actitivies = []

        for chore in chores:
            try:
                new_time_plan_activity = TimePlanActivity.new_activity_for_chore(
                    context.domain_context,
                    time_plan_ref_id=args.ref_id,
                    chore_ref_id=chore.ref_id,
                    kind=args.kind,
                    feasability=args.feasability,
                )
                new_time_plan_activity = await self.create_entity(
                    context.domain_context,
                    uow,
                    progress_reporter,
                    context.user.ref_id,
                    new_time_plan_activity,
                )
                new_time_plan_actitivies.append(new_time_plan_activity)
            except TimePlanAlreadyAssociatedWithTargetError:
                # We were already working on this chore, no need to panic
                pass

            # The inbox tasks the chore already generated in the interval of the
            # time plan become activities of their own.
            inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=None,
                allow_archived=False,
                owner=EntityLink.std(NamedEntityTag.CHORE.value, chore.ref_id),
            )

            for inbox_task in inbox_tasks:
                if not inbox_task_overlaps_time_plan(inbox_task, time_plan):
                    continue

                try:
                    new_inbox_task_activity = (
                        TimePlanActivity.new_activity_for_inbox_task(
                            context.domain_context,
                            time_plan_ref_id=args.ref_id,
                            inbox_task_ref_id=inbox_task.ref_id,
                            kind=args.kind,
                            feasability=args.feasability,
                        )
                    )
                    new_inbox_task_activity = await self.create_entity(
                        context.domain_context,
                        uow,
                        progress_reporter,
                        context.user.ref_id,
                        new_inbox_task_activity,
                    )
                    new_time_plan_actitivies.append(new_inbox_task_activity)
                except TimePlanAlreadyAssociatedWithTargetError:
                    # We were already working on this task, no need to panic
                    pass

        return TimePlanAssociateWithChoresResult(
            new_time_plan_activities=new_time_plan_actitivies
        )

    async def _perform_post_transactional_mutation_work(
        self,
        progress_reporter: ProgressReporter,
        context: JupiterLoggedInMutationContext,
        args: TimePlanAssociateWithChoresArgs,
        result: TimePlanAssociateWithChoresResult,
    ) -> None:
        """Generate inbox tasks covering the time plan, then attach the new ones."""
        async with self._ports.domain_storage_engine.get_unit_of_work() as uow:
            time_plan = await uow.get_for(TimePlan).load_by_id(args.ref_id)

        gen_service = GenService(
            self._ports.domain_storage_engine,
            self._concept_registry,
        )
        for day in dates_in_inclusive_range(time_plan.start_date, time_plan.end_date):
            await gen_service.do_it(
                context.domain_context,
                progress_reporter=progress_reporter,
                user=context.user,
                workspace=context.workspace,
                gen_even_if_not_modified=False,
                today=day,
                gen_targets=[SyncTarget.CHORES],
                period=None,
                filter_chore_ref_ids=args.chore_ref_ids,
            )

        async with self._ports.domain_storage_engine.get_unit_of_work() as uow:
            for chore_ref_id in args.chore_ref_ids:
                inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                    parent_ref_id=None,
                    allow_archived=False,
                    owner=EntityLink.std(NamedEntityTag.CHORE.value, chore_ref_id),
                )
                for inbox_task in inbox_tasks:
                    if not inbox_task_overlaps_time_plan(inbox_task, time_plan):
                        continue
                    try:
                        new_inbox_task_activity = (
                            TimePlanActivity.new_activity_for_inbox_task(
                                context.domain_context,
                                time_plan_ref_id=time_plan.ref_id,
                                inbox_task_ref_id=inbox_task.ref_id,
                                kind=args.kind,
                                feasability=args.feasability,
                            )
                        )
                        await self.create_entity(
                            context.domain_context,
                            uow,
                            progress_reporter,
                            context.user.ref_id,
                            new_inbox_task_activity,
                        )
                    except TimePlanAlreadyAssociatedWithTargetError:
                        pass
