"""The command for removeing all branch and leaf type entities."""
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
from jupiter.core.domain.gamification.score_log import ScoreLog
from jupiter.core.domain.gamification.score_log_entry import ScoreLogEntry
from jupiter.core.domain.gamification.score_period_best import (
    ScorePeriodBestRepository,
)
from jupiter.core.domain.gamification.score_stats import (
    ScoreStatsRepository,
)
from jupiter.core.domain.gc.gc_log import GCLog
from jupiter.core.domain.gen.gen_log import GenLog
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.habits.service.remove_service import HabitRemoveService
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.service.remove_service import (
    InboxTaskRemoveService,
)
from jupiter.core.domain.infra.generic_crown_remover import generic_crown_remover
from jupiter.core.domain.infra.generic_destroyer import generic_destroyer
from jupiter.core.domain.journals.journal_collection import JournalCollection
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.metrics.service.remove_service import MetricRemoveService
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.persons.service.remove_service import PersonRemoveService
from jupiter.core.domain.projects.project import Project, ProjectRepository
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.domain.projects.service.remove_service import ProjectRemoveService
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.push_integrations.email.service.remove_service import (
    EmailTaskRemoveService,
)
from jupiter.core.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.push_integrations.slack.service.remove_service import (
    SlackTaskRemoveService,
)
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
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
from jupiter.core.domain.user_workspace_link.user_workspace_link import UserWorkspaceLink, UserWorkspaceLinkRepository
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.domain.vacations.vacation_collection import VacationCollection
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)
from jupiter.core.utils.feature_flag_controls import infer_feature_flag_controls


@use_case_args
class RemoveAllArgs(UseCaseArgsBase):
    """PersonFindArgs."""


@mutation_use_case()
class RemoveAllUseCase(AppLoggedInMutationUseCase[RemoveAllArgs, None]):
    """The command for removeing all branch and leaf type entities."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: RemoveAllArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            user_workspace_link = await uow.get(UserWorkspaceLinkRepository).load_by_user(user.ref_id)
            await uow.get_for(UserWorkspaceLink).remove(user_workspace_link.ref_id)

            await generic_destroyer(context.domain_context, uow, Workspace, workspace.ref_id)
            await generic_destroyer(context.domain_context, uow, User, user.ref_id)

        async with self._use_case_storage_engine.get_unit_of_work() as uc_uow:
            await uc_uow.mutation_use_case_invocation_record_repository.clear_all(workspace.ref_id)

        async with self._search_storage_engine.get_unit_of_work() as search_uow:
            await search_uow.search_repository.drop(workspace.ref_id)
