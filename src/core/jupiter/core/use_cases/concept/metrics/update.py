"""The command for updating a metric's properties."""
import typing

from jupiter.core.domain.application.gen.service.gen_service import GenService
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.concept.metrics.metric import Metric
from jupiter.core.domain.concept.metrics.metric_collection import MetricCollection
from jupiter.core.domain.concept.metrics.metric_name import MetricName
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class MetricUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[MetricName]
    icon: UpdateAction[EntityIcon | None]
    collection_period: UpdateAction[RecurringTaskPeriod | None]
    collection_eisen: UpdateAction[Eisen | None]
    collection_difficulty: UpdateAction[Difficulty | None]
    collection_actionable_from_day: UpdateAction[RecurringTaskDueAtDay | None]
    collection_actionable_from_month: UpdateAction[RecurringTaskDueAtMonth | None]
    collection_due_at_day: UpdateAction[RecurringTaskDueAtDay | None]
    collection_due_at_month: UpdateAction[RecurringTaskDueAtMonth | None]


@mutation_use_case(WorkspaceFeature.METRICS)
class MetricUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[MetricUpdateArgs, None]
):
    """The command for updating a metric's properties."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: MetricUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        metric_collection = await uow.get_for(MetricCollection).load_by_parent(
            workspace.ref_id,
        )
        metric = await uow.get_for(Metric).load_by_id(
            args.ref_id,
        )

        # Change the metrics
        collection_params: UpdateAction[RecurringTaskGenParams | None]
        if (
            args.collection_period.should_change
            or args.collection_eisen.should_change
            or args.collection_difficulty.should_change
            or args.collection_actionable_from_day.should_change
            or args.collection_actionable_from_month.should_change
            or args.collection_due_at_day.should_change
            or args.collection_due_at_month
        ):
            new_collection_period = None
            if args.collection_period.should_change:
                new_collection_period = args.collection_period.just_the_value
            elif metric.collection_params is not None:
                new_collection_period = metric.collection_params.period

            if new_collection_period is not None:
                new_collection_eisen = Eisen.REGULAR
                if args.collection_eisen.should_change:
                    new_collection_eisen = (
                        args.collection_eisen.just_the_value or Eisen.REGULAR
                    )
                elif metric.collection_params is not None:
                    new_collection_eisen = metric.collection_params.eisen

                new_collection_difficulty = Difficulty.EASY
                if args.collection_difficulty.should_change:
                    new_collection_difficulty = (
                        args.collection_difficulty.just_the_value or Difficulty.EASY
                    )
                elif metric.collection_params is not None:
                    new_collection_difficulty = metric.collection_params.difficulty

                new_collection_actionable_from_day = None
                if args.collection_actionable_from_day.should_change:
                    new_collection_actionable_from_day = (
                        args.collection_actionable_from_day.just_the_value
                    )
                elif metric.collection_params is not None:
                    new_collection_actionable_from_day = (
                        metric.collection_params.actionable_from_day
                    )

                new_collection_actionable_from_month = None
                if args.collection_actionable_from_month.should_change:
                    new_collection_actionable_from_month = (
                        args.collection_actionable_from_month.just_the_value
                    )
                elif metric.collection_params is not None:
                    new_collection_actionable_from_month = (
                        metric.collection_params.actionable_from_month
                    )

                new_collection_due_at_day = None
                if args.collection_due_at_day.should_change:
                    new_collection_due_at_day = (
                        args.collection_due_at_day.just_the_value
                    )
                elif metric.collection_params is not None:
                    new_collection_due_at_day = metric.collection_params.due_at_day

                new_collection_due_at_month = None
                if args.collection_due_at_month.should_change:
                    new_collection_due_at_month = (
                        args.collection_due_at_month.just_the_value
                    )
                elif metric.collection_params is not None:
                    new_collection_due_at_month = metric.collection_params.due_at_month

                collection_params = UpdateAction.change_to(
                    RecurringTaskGenParams(
                        period=new_collection_period,
                        eisen=new_collection_eisen,
                        difficulty=new_collection_difficulty,
                        actionable_from_day=new_collection_actionable_from_day,
                        actionable_from_month=new_collection_actionable_from_month,
                        due_at_day=new_collection_due_at_day,
                        due_at_month=new_collection_due_at_month,
                    ),
                )
            else:
                collection_params = UpdateAction.change_to(None)
        else:
            collection_params = UpdateAction.do_nothing()

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            workspace.ref_id,
        )

        metric_collection_tasks = await uow.get_for(InboxTask).find_all_generic(
            parent_ref_id=inbox_task_collection.ref_id,
            source=[InboxTaskSource.METRIC],
            allow_archived=True,
            metric_ref_id=[metric.ref_id],
        )

        metric = metric.update(
            context.domain_context,
            name=args.name,
            icon=args.icon,
            collection_params=collection_params,
        )

        await uow.get_for(Metric).save(metric)
        await progress_reporter.mark_updated(metric)

        # Change the inbox tasks
        if metric.collection_params is None:
            # Situation 1: we need to get rid of any existing collection metrics because there's no collection anymore.
            inbox_task_archive_service = InboxTaskArchiveService()
            for inbox_task in metric_collection_tasks:
                await inbox_task_archive_service.do_it(
                    context.domain_context, uow, progress_reporter, inbox_task
                )
        else:
            # Situation 2: we need to update the existing metrics.
            project = await uow.get_for(Project).load_by_id(
                metric_collection.collection_project_ref_id,
            )

            for inbox_task in metric_collection_tasks:
                schedule = schedules.get_schedule(
                    metric.collection_params.period,
                    metric.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now),
                    None,
                    metric.collection_params.actionable_from_day,
                    metric.collection_params.actionable_from_month,
                    metric.collection_params.due_at_day,
                    metric.collection_params.due_at_month,
                )

                inbox_task = inbox_task.update_link_to_metric(
                    ctx=context.domain_context,
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    recurring_timeline=schedule.timeline,
                    eisen=metric.collection_params.eisen,
                    difficulty=metric.collection_params.difficulty,
                    actionable_date=schedule.actionable_date,
                    due_time=schedule.due_date,
                )

                await uow.get_for(InboxTask).save(inbox_task)
                await progress_reporter.mark_updated(inbox_task)

    async def _perform_post_mutation_work(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: MetricUpdateArgs,
        result: None,
    ) -> None:
        """Execute the command's post-mutation work."""
        await GenService(self._domain_storage_engine).do_it(
            context.domain_context,
            progress_reporter=progress_reporter,
            user=context.user,
            workspace=context.workspace,
            gen_even_if_not_modified=False,
            today=self._time_provider.get_current_date(),
            gen_targets=[SyncTarget.METRICS],
            period=[args.collection_period.just_the_value]
            if (
                args.collection_period.should_change
                and args.collection_period.just_the_value is not None
            )
            else None,
            filter_metric_ref_ids=[args.ref_id],
        )
