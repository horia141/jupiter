"""Update settings around journals."""

from typing import cast

from jupiter.core.domain.application.gen.service.gen_service import GenService
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.journals.journal import Journal, JournalRepository
from jupiter.core.domain.concept.journals.journal_collection import JournalCollection
from jupiter.core.domain.concept.journals.journal_generation_approach import (
    JournalGenerationApproach,
)
from jupiter.core.domain.concept.journals.journal_source import JournalSource
from jupiter.core.domain.concept.projects.project import Project
from jupiter.core.domain.concept.projects.project_collection import ProjectCollection
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.archival_reason import ArchivalReason
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_crown_archiver import generic_crown_archiver
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInMutationUseCaseContext,
    mutation_use_case,
)


@use_case_args
class JournalUpdateSettingsArgs(UseCaseArgsBase):
    """Args."""

    periods: UpdateAction[list[RecurringTaskPeriod]]
    generation_approach: UpdateAction[JournalGenerationApproach]
    generation_in_advance_days: UpdateAction[dict[RecurringTaskPeriod, int]]
    writing_task_project_ref_id: UpdateAction[EntityId | None]
    writing_task_eisen: UpdateAction[Eisen | None]
    writing_task_difficulty: UpdateAction[Difficulty | None]


@mutation_use_case(WorkspaceFeature.JOURNALS)
class JournalUpdateSettingsUseCase(
    AppLoggedInMutationUseCase[JournalUpdateSettingsArgs, None]
):
    """Command for updating the settings for journals in general."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: JournalUpdateSettingsArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            workspace = context.workspace

            journal_collection = await uow.get_for(JournalCollection).load_by_parent(
                workspace.ref_id
            )
            inbox_task_collection = await uow.get_for(
                InboxTaskCollection
            ).load_by_parent(workspace.ref_id)
            project_collection = await uow.get_for(ProjectCollection).load_by_parent(
                workspace.ref_id
            )

            if workspace.is_feature_available(WorkspaceFeature.PROJECTS):
                if args.writing_task_project_ref_id.test(lambda x: x is None):
                    raise Exception("Writing task project ref id is required")
                if args.writing_task_project_ref_id.should_change:
                    project = await uow.get_for(Project).load_by_id(
                        cast(EntityId, args.writing_task_project_ref_id.just_the_value)
                    )
                    writing_task_project_ref_id = UpdateAction.change_to(
                        project.ref_id
                    )
                else:
                    writing_task_project_ref_id = UpdateAction.do_nothing()
            else:
                root_project = await uow.get_for(Project).find_all_generic(
                    parent_ref_id=project_collection.ref_id,
                    allow_archived=False,
                    parent_project_ref_id=None,
                )
                if len(root_project) != 1:
                    raise Exception("Root project not found")
                writing_task_project_ref_id = UpdateAction.change_to(
                    root_project[0].ref_id
                )

            journal_collection = journal_collection.update(
                context.domain_context,
                periods=args.periods.transform(lambda s: set(s)),
                generation_approach=args.generation_approach,
                generation_in_advance_days=args.generation_in_advance_days,
                writing_task_project_ref_id=writing_task_project_ref_id,
                writing_task_eisen=args.writing_task_eisen,
                writing_task_difficulty=args.writing_task_difficulty,
            )
            await uow.get_for(JournalCollection).save(journal_collection)

        gen_service = GenService(
            domain_storage_engine=self._domain_storage_engine,
        )

        await gen_service.do_it(
            ctx=context.domain_context,
            progress_reporter=progress_reporter,
            user=context.user,
            workspace=context.workspace,
            gen_even_if_not_modified=True,
            today=self._time_provider.get_current_date(),
            gen_targets=[SyncTarget.JOURNALS],
            period=None,
        )

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            for period in RecurringTaskPeriod:
                schedule = schedules.get_schedule(
                    period=period,
                    name=EntityName("Test"),
                    right_now=self._time_provider.get_current_date().to_timestamp_at_end_of_day(),
                )

                journals_for_period = await uow.get(JournalRepository).find_all_in_range(
                    parent_ref_id=journal_collection.ref_id,
                    allow_archived=False,
                    filter_periods=[period],
                    filter_start_date=schedule.first_day,
                    filter_end_date=schedule.end_day.add_days(
                        365
                    ),  # Look reasonably far in the future
                )

                for journal in journals_for_period:
                    if journal.source == JournalSource.USER:
                        continue

                    writing_tasks = await uow.get_for(InboxTask).find_all_generic(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=False,
                        source=InboxTaskSource.JOURNAL,
                        source_entity_ref_id=journal.ref_id,
                    )

                    writing_task: InboxTask | None
                    if len(writing_tasks) == 0:
                        writing_task = None
                    elif len(writing_tasks) == 1:
                        writing_task = writing_tasks[0]
                    else:
                        raise Exception("Found multiple writing tasks for journal")

                    if (
                        period not in journal_collection.periods
                        or journal_collection.generation_approach.should_not_generate_a_journal
                    ):
                        await generic_crown_archiver(
                            context.domain_context,
                            uow,
                            progress_reporter,
                            Journal,
                            journal.ref_id,
                            ArchivalReason.USER,
                        )
                    if (
                        writing_task
                        and journal_collection.generation_approach.should_not_generate_a_writing_task
                    ):
                        await generic_crown_archiver(
                            context.domain_context,
                            uow,
                            progress_reporter,
                            InboxTask,
                            writing_task.ref_id,
                            ArchivalReason.USER,
                        ) 