"""UseCase for creating recurring tasks."""
from argparse import ArgumentParser, Namespace
from typing import Final

from jupiter.core.framework.realm import RealmCodecRegistry

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.use_cases.gen.do import GenDoArgs, GenDoUseCase
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.utils.global_properties import GlobalProperties
from jupiter.core.utils.time_provider import TimeProvider


class GenDo(LoggedInMutationCommand[GenDoUseCase]):
    """UseCase class for creating recurring tasks."""

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]

    def __init__(
        self,
        global_properties: GlobalProperties,
        time_provider: TimeProvider,
        realm_codec_registry: RealmCodecRegistry,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        use_case: GenDoUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(realm_codec_registry, session_storage, top_level_context, use_case)
        self._global_properties = global_properties
        self._time_provider = time_provider

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--today", help="The date on which the upsert should run at"
        )
        parser.add_argument(
            "--target",
            dest="gen_targets",
            default=[],
            action="append",
            choices=[
                s.value
                for s in self._top_level_context.workspace.infer_sync_targets_for_enabled_features(
                    None
                )
            ],
            help="What exactly to try to generate for",
        )
        parser.add_argument(
            "--period",
            default=[RecurringTaskPeriod.DAILY.value],
            action="append",
            choices=RecurringTaskPeriod.all_values(),
            help="The period for which the upsert should happen. Defaults to all",
        )
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.PROJECTS
        ):
            parser.add_argument(
                "--project-id",
                dest="project_ref_ids",
                default=[],
                action="append",
                help="Allow only tasks from this project",
            )
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.HABITS
        ):
            parser.add_argument(
                "--habit-id",
                dest="habit_ref_ids",
                default=[],
                action="append",
                help="Allow only habits with this id",
            )
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.CHORES
        ):
            parser.add_argument(
                "--chore-id",
                dest="chore_ref_ids",
                default=[],
                action="append",
                help="Allow only chores with this id",
            )
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.METRICS
        ):
            parser.add_argument(
                "--metric-id",
                dest="metric_ref_ids",
                default=[],
                action="append",
                help="Allow only these metrics",
            )
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.PERSONS
        ):
            parser.add_argument(
                "--person-id",
                dest="person_ref_ids",
                default=[],
                action="append",
                help="Allow only these persons",
            )
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.SLACK_TASKS
        ):
            parser.add_argument(
                "--slack-task-id",
                dest="slack_task_ref_ids",
                default=[],
                action="append",
                help="Allow only these Slack tasks",
            )
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.EMAIL_TASKS
        ):
            parser.add_argument(
                "--email-task-id",
                dest="email_task_ref_ids",
                default=[],
                action="append",
                help="Allow only these email tasks",
            )
        parser.add_argument(
            "--ignore-modified-times",
            dest="gen_even_if_not_modified",
            action="store_true",
            default=False,
            help="Generate even if modification times would say otherwise",
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        today = (
            ADate.from_raw_in_tz(self._global_properties.timezone, args.today)
            if args.today
            else self._time_provider.get_current_date()
        )
        gen_targets = (
            [SyncTarget.from_raw(st) for st in args.gen_targets]
            if len(args.gen_targets) > 0
            else None
        )
        period = (
            [RecurringTaskPeriod.from_raw(p) for p in args.period]
            if len(args.period) > 0
            else None
        )
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.PROJECTS
        ):
            project_ref_ids = (
                [EntityId.from_raw(pk) for pk in args.project_ref_ids]
                if len(args.project_ref_ids) > 0
                else None
            )
        else:
            project_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.HABITS
        ):
            habit_ref_ids = (
                [EntityId.from_raw(rid) for rid in args.habit_ref_ids]
                if len(args.habit_ref_ids) > 0
                else None
            )
        else:
            habit_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.CHORES
        ):
            chore_ref_ids = (
                [EntityId.from_raw(rid) for rid in args.chore_ref_ids]
                if len(args.chore_ref_ids) > 0
                else None
            )
        else:
            chore_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.METRICS
        ):
            metric_ref_ids = (
                [EntityId.from_raw(mk) for mk in args.metric_ref_ids]
                if len(args.metric_ref_ids) > 0
                else None
            )
        else:
            metric_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.PERSONS
        ):
            person_ref_ids = (
                [EntityId.from_raw(rid) for rid in args.person_ref_ids]
                if len(args.person_ref_ids) > 0
                else None
            )
        else:
            person_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.SLACK_TASKS
        ):
            slack_task_ref_ids = (
                [EntityId.from_raw(rid) for rid in args.slack_task_ref_ids]
                if len(args.slack_task_ref_ids) > 0
                else None
            )
        else:
            slack_task_ref_ids = None
        if self._top_level_context.workspace.is_feature_available(
            WorkspaceFeature.EMAIL_TASKS
        ):
            email_task_ref_ids = (
                [EntityId.from_raw(rid) for rid in args.email_task_ref_ids]
                if len(args.email_task_ref_ids) > 0
                else None
            )
        else:
            email_task_ref_ids = None
        gen_even_if_not_modified: bool = args.gen_even_if_not_modified

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            GenDoArgs(
                source=EventSource.CLI,
                gen_even_if_not_modified=gen_even_if_not_modified,
                today=today,
                gen_targets=gen_targets,
                period=period,
                filter_project_ref_ids=project_ref_ids,
                filter_habit_ref_ids=habit_ref_ids,
                filter_chore_ref_ids=chore_ref_ids,
                filter_metric_ref_ids=metric_ref_ids,
                filter_person_ref_ids=person_ref_ids,
                filter_slack_task_ref_ids=slack_task_ref_ids,
                filter_email_task_ref_ids=email_task_ref_ids,
            ),
        )
