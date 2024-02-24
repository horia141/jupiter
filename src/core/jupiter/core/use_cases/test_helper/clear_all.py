"""The command for clearing all branch and leaf type entities."""

from jupiter.core.domain.auth.auth import Auth
from jupiter.core.domain.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.auth.password_plain import PasswordPlain
from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.big_plans.service.remove_service import BigPlanRemoveService
from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.chores.chore_collection import ChoreCollection
from jupiter.core.domain.chores.service.remove_service import ChoreRemoveService
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.service.note_remove_service import NoteRemoveService
from jupiter.core.domain.core.timezone import Timezone
from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.docs.doc_collection import DocCollection
from jupiter.core.domain.docs.service.doc_remove_service import DocRemoveService
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.gamification.infra.score_period_best_repository import ScorePeriodBestRepository
from jupiter.core.domain.gamification.infra.score_stats_repository import ScoreStatsRepository
from jupiter.core.domain.gamification.score_log import ScoreLog
from jupiter.core.domain.gamification.score_log_entry import ScoreLogEntry
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.habits.service.remove_service import HabitRemoveService
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.infra.generic_remover import generic_remover
from jupiter.core.domain.metrics.infra.metric_collection_repository import MetricCollectionRepository
from jupiter.core.domain.metrics.infra.metric_repository import MetricRepository
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.metrics.service.remove_service import MetricRemoveService
from jupiter.core.domain.persons.infra.person_collection_repository import PersonCollectionRepository
from jupiter.core.domain.persons.infra.person_repository import PersonRepository
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.persons.service.remove_service import PersonRemoveService
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.projects.service.remove_service import ProjectRemoveService
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.email.email_task_collection import EmailTaskCollection
from jupiter.core.domain.push_integrations.email.service.remove_service import (
    EmailTaskRemoveService,
)
from jupiter.core.domain.push_integrations.group.push_integration_group import PushIntegrationGroup
from jupiter.core.domain.push_integrations.slack.service.remove_service import (
    SlackTaskRemoveService,
)
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.push_integrations.slack.slack_task_collection import SlackTaskCollection
from jupiter.core.domain.smart_lists.service.remove_service import (
    SmartListRemoveService,
)
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.core.domain.storage_engine import (
    DomainUnitOfWork,
)
from jupiter.core.domain.user.user import User
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.domain.vacations.vacation_collection import VacationCollection
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.base.entity_id import EntityId
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
from jupiter.core.utils.feature_flag_controls import infer_feature_flag_controls


@use_case_args
class ClearAllArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    user_name: UserName
    user_timezone: Timezone
    user_feature_flags: set[UserFeature]
    auth_current_password: PasswordPlain
    auth_new_password: PasswordNewPlain
    auth_new_password_repeat: PasswordNewPlain
    workspace_name: WorkspaceName
    workspace_default_project_ref_id: EntityId
    workspace_feature_flags: set[WorkspaceFeature]


@mutation_use_case()
class ClearAllUseCase(AppTransactionalLoggedInMutationUseCase[ClearAllArgs, None]):
    """The command for clearing all branch and leaf type entities."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ClearAllArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user

        score_log = await uow.repository_for(ScoreLog).load_by_parent(user.ref_id)

        workspace = context.workspace
        (
            user_feature_flags_controls,
            workspace_feature_flags_controls,
        ) = infer_feature_flag_controls(self._global_properties)

        inbox_task_collection = (
            await uow.repository_for(InboxTaskCollection).load_by_parent(
                workspace.ref_id,
            )
        )
        habit_collection = await uow.repository_for(HabitCollection).load_by_parent(
            workspace.ref_id,
        )
        chore_collection = await uow.repository_for(ChoreCollection).load_by_parent(
            workspace.ref_id,
        )
        big_plan_collection = await uow.repository_for(BigPlanCollection).load_by_parent(
            workspace.ref_id,
        )
        doc_collection = await uow.repository_for(DocCollection).load_by_parent(
            workspace.ref_id
        )
        vacation_collection = await uow.repository_for(VacationCollection).load_by_parent(
            workspace.ref_id,
        )
        project_collection = await uow.repository_for(ProjectCollection).load_by_parent(
            workspace.ref_id,
        )
        smart_list_collection = (
            await uow.repository_for(SmartListCollection).load_by_parent(
                workspace.ref_id,
            )
        )
        metric_collection = await uow.repository_for(MetricCollection).load_by_parent(
            workspace.ref_id,
        )
        person_collection = await uow.repository_for(PersonCollection).load_by_parent(
            workspace.ref_id,
        )
        push_integration_group = (
            await uow.repository_for(PushIntegrationGroup).load_by_parent(
                workspace.ref_id,
            )
        )
        slack_task_collection = (
            await uow.repository_for(SlackTaskCollection).load_by_parent(
                push_integration_group.ref_id,
            )
        )
        email_task_collection = (
            await uow.repository_for(EmailTaskCollection).load_by_parent(
                push_integration_group.ref_id,
            )
        )
        note_collection = await uow.repository_for(NoteCollection).load_by_parent(
            workspace.ref_id
        )

        user_feature_flags = {}
        for user_feature in UserFeature:
            user_feature_flags[user_feature] = user_feature in args.user_feature_flags

        workspace_feature_flags = {}
        for workspace_feature in WorkspaceFeature:
            workspace_feature_flags[workspace_feature] = (
                workspace_feature in args.workspace_feature_flags
            )

        async with progress_reporter.section("Resseting user"):
            user = user.update(
                ctx=context.domain_context,
                name=UpdateAction.change_to(args.user_name),
                timezone=UpdateAction.change_to(args.user_timezone),
            )

            user = user.change_feature_flags(
                ctx=context.domain_context,
                feature_flag_controls=user_feature_flags_controls,
                feature_flags=user_feature_flags,
            )
            await uow.repository_for(User).save(user)

            auth = await uow.repository_for(Auth).load_by_parent(parent_ref_id=user.ref_id)
            auth = auth.change_password(
                ctx=context.domain_context,
                current_password=args.auth_current_password,
                new_password=args.auth_new_password,
                new_password_repeat=args.auth_new_password_repeat,
            )
            await uow.repository_for(Auth).save(auth)

        async with progress_reporter.section("Resetting score log"):
            all_score_log_entries = await uow.repository_for(ScoreLogEntry).find_all(
                parent_ref_id=score_log.ref_id,
                allow_archived=True,
            )

            for score_log_entry in all_score_log_entries:
                await uow.repository_for(ScoreLogEntry).remove(score_log_entry.ref_id)

            all_score_stats = await uow.get_r(ScoreStatsRepository).find_all(
                score_log.ref_id
            )

            for score_stats in all_score_stats:
                await uow.get_r(ScoreStatsRepository).remove(score_stats.key)

            all_period_bests = await uow.get_r(ScorePeriodBestRepository).find_all(
                score_log.ref_id
            )

            for period_best in all_period_bests:
                await uow.get_r(ScorePeriodBestRepository).remove(period_best.key)

        async with progress_reporter.section("Resetting workspace"):
            default_project = await uow.repository_for(Project).load_by_id(
                args.workspace_default_project_ref_id,
            )

            workspace = workspace.update(
                ctx=context.domain_context,
                name=UpdateAction.change_to(args.workspace_name),
            )

            workspace = workspace.change_default_project(
                ctx=context.domain_context,
                default_project_ref_id=default_project.ref_id,
            )
            workspace = workspace.change_feature_flags(
                ctx=context.domain_context,
                feature_flag_controls=workspace_feature_flags_controls,
                feature_flags=workspace_feature_flags,
            )

            await uow.repository_for(Workspace).save(workspace)

        async with progress_reporter.section("Clearing habits"):
            all_habits = await uow.repository_for(Habit).find_all(
                parent_ref_id=habit_collection.ref_id,
                allow_archived=True,
            )
            habit_remove_service = HabitRemoveService()
            for habit in all_habits:
                await habit_remove_service.remove(
                    context.domain_context, uow, progress_reporter, habit.ref_id
                )

        async with progress_reporter.section("Clearing chores"):
            all_chores = await uow.repository_for(Chore).find_all(
                parent_ref_id=chore_collection.ref_id,
                allow_archived=True,
            )
            chore_remove_service = ChoreRemoveService()
            for chore in all_chores:
                await chore_remove_service.remove(
                    context.domain_context, uow, progress_reporter, chore.ref_id
                )

        async with progress_reporter.section("Clearing big plans"):
            all_big_plans = await uow.repository_for(BigPlan).find_all(
                parent_ref_id=big_plan_collection.ref_id,
                allow_archived=True,
            )
            big_plan_remove_service = BigPlanRemoveService()
            for big_plan in all_big_plans:
                await big_plan_remove_service.remove(
                    context.domain_context,
                    uow,
                    progress_reporter,
                    workspace,
                    big_plan.ref_id,
                )

        async with progress_reporter.section("Clearing docs"):
            root_docs = await uow.repository_for(Doc).find_all_with_filters(
                parent_ref_id=doc_collection.ref_id,
                allow_archived=True,
                filter_parent_doc_ref_ids=[None],
            )
            doc_remove_service = DocRemoveService()
            for doc in root_docs:
                await doc_remove_service.do_it(
                    context.domain_context, uow, progress_reporter, doc
                )

        async with progress_reporter.section("Clearing vacations"):
            all_vacations = await uow.repository_for(Vacation).find_all(
                parent_ref_id=vacation_collection.ref_id,
                allow_archived=True,
            )

            for vacation in all_vacations:
                await generic_remover(
                    context.domain_context,
                    uow,
                    progress_reporter,
                    Vacation,
                    vacation.ref_id,
                )

        async with progress_reporter.section("Clearing projects"):
            all_projects = await uow.repository_for(Project).find_all(
                parent_ref_id=project_collection.ref_id,
                allow_archived=True,
            )

            project_remove_service = ProjectRemoveService()
            for project in all_projects:
                if project.ref_id == args.workspace_default_project_ref_id:
                    continue
                await project_remove_service.do_it(
                    context.domain_context,
                    uow,
                    progress_reporter,
                    workspace,
                    project.ref_id,
                )

        async with progress_reporter.section("Clearing smart lists"):
            all_smart_lists = await uow.repository_for(SmartList).find_all(
                parent_ref_id=smart_list_collection.ref_id,
                allow_archived=True,
            )
            smart_list_remove_service = SmartListRemoveService()
            for smart_list in all_smart_lists:
                await smart_list_remove_service.execute(
                    context.domain_context,
                    uow,
                    progress_reporter,
                    smart_list,
                )

        async with progress_reporter.section("Clearing metrics"):
            all_metrics = await uow.repository_for(Metric).find_all(
                parent_ref_id=metric_collection.ref_id,
                allow_archived=True,
            )

            metric_collection = metric_collection.change_collection_project(
                context.domain_context,
                collection_project_ref_id=default_project.ref_id,
            )

            await uow.repository_for(MetricCollection).save(metric_collection)

            metric_remove_service = MetricRemoveService()
            for metric in all_metrics:
                await metric_remove_service.execute(
                    context.domain_context,
                    uow,
                    progress_reporter,
                    workspace,
                    metric,
                )

        async with progress_reporter.section("Clearing person"):
            all_persons = await uow.repository_for(Person).find_all(
                parent_ref_id=person_collection.ref_id,
                allow_archived=True,
            )

            person_collection = person_collection.change_catch_up_project(
                context.domain_context,
                catch_up_project_ref_id=default_project.ref_id,
            )

            await uow.repository_for(PersonCollection).save(person_collection)

            person_remove_service = PersonRemoveService()
            for person in all_persons:
                await person_remove_service.do_it(
                    context.domain_context,
                    uow,
                    progress_reporter,
                    person_collection,
                    person,
                )

        async with progress_reporter.section("Clearing Slack tasks"):
            all_slack_tasks = await uow.repository_for(SlackTask).find_all(
                parent_ref_id=slack_task_collection.ref_id,
                allow_archived=True,
            )
            slack_task_collection = slack_task_collection.change_generation_project(
                context.domain_context,
                generation_project_ref_id=default_project.ref_id,
            )

            await uow.repository_for(SlackTaskCollection).save(slack_task_collection)

            slack_task_remove_service = SlackTaskRemoveService()
            for slack_task in all_slack_tasks:
                await slack_task_remove_service.do_it(
                    context.domain_context, uow, progress_reporter, slack_task
                )

        async with progress_reporter.section("Clearing email tasks"):
            all_email_tasks = await uow.repository_for(EmailTask).find_all(
                parent_ref_id=email_task_collection.ref_id,
                allow_archived=True,
            )
            email_task_collection = email_task_collection.change_generation_project(
                context.domain_context,
                generation_project_ref_id=default_project.ref_id,
            )

            await uow.repository_for(EmailTaskCollection).save(email_task_collection)

            email_task_remove_service = EmailTaskRemoveService()
            for email_task in all_email_tasks:
                await email_task_remove_service.do_it(
                    context.domain_context, uow, progress_reporter, email_task
                )

        async with progress_reporter.section("Clearing inbox tasks"):
            all_inbox_tasks = await uow.repository_for(InboxTask).find_all(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
            )
            inbox_task_remove_service = InboxTaskRemoveService()
            for inbox_task in all_inbox_tasks:
                await inbox_task_remove_service.do_it(
                    context.domain_context, uow, progress_reporter, inbox_task
                )

        async with progress_reporter.section("Clearing notes"):
            root_notes = await uow.repository_for(Note).find_all(
                parent_ref_id=note_collection.ref_id,
                allow_archived=True,
            )
            note_remove_service = NoteRemoveService()
            for note in root_notes:
                await note_remove_service.remove(context.domain_context, uow, note)

        async with progress_reporter.section("Clearing use case invocation records"):
            async with self._use_case_storage_engine.get_unit_of_work() as uc_uow:
                await uc_uow.mutation_use_case_invocation_record_repository.clear_all()

        async with progress_reporter.section("Clearing the search index"):
            async with self._search_storage_engine.get_unit_of_work() as search_uow:
                await search_uow.search_repository.drop()
