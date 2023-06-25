"""Helpers for console rendering."""
import argparse
import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncIterator, DefaultDict, Final, Iterator, List, Optional, Tuple

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.difficulty import Difficulty
from jupiter.core.domain.eisen import Eisen
from jupiter.core.domain.email_address import EmailAddress
from jupiter.core.domain.entity_name import EntityName
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.metrics.metric_unit import MetricUnit
from jupiter.core.domain.persons.person_birthday import PersonBirthday
from jupiter.core.domain.persons.person_relationship import PersonRelationship
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.domain.push_integrations.email.email_user_name import EmailUserName
from jupiter.core.domain.push_integrations.slack.slack_channel_name import (
    SlackChannelName,
)
from jupiter.core.domain.push_integrations.slack.slack_user_name import SlackUserName
from jupiter.core.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.core.domain.timezone import Timezone
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    EntityProgressReporter,
    MarkProgressStatus,
    ProgressReporterFactory,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseContext
from jupiter.core.utils.progress_reporter import NoOpContextProgressReporter
from rich.console import Console
from rich.control import Control
from rich.panel import Panel
from rich.status import Status
from rich.text import Text
from rich.tree import Tree


class RichConsoleEntityProgressReporter(EntityProgressReporter):
    """A progress reporter for a particular entity."""

    _console: Final[Console]
    _status: Final[Status]
    _entity_type: Final[str]
    _action_type: Final[str]
    _entity_id: Optional[EntityId]
    _entity_name: Optional[str]
    _local_change_status: Optional[MarkProgressStatus]
    _remote_change_status: Optional[MarkProgressStatus]
    _progresses: Final[List[Tuple[str, MarkProgressStatus]]]
    _print_indent: Final[int]
    _is_needed: bool

    def __init__(
        self,
        console: Console,
        status: Status,
        entity_type: str,
        action_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
        print_indent: int = 0,
    ) -> None:
        """Constructor."""
        self._console = console
        self._status = status
        self._entity_type = entity_type
        self._action_type = action_type
        self._entity_id = entity_id
        self._entity_name = entity_name
        self._local_change_status = None
        self._remote_change_status = None
        self._progresses = []
        self._print_indent = print_indent
        self._is_needed = True

    async def mark_not_needed(self) -> EntityProgressReporter:
        """Mark the fact that a particular modification isn't needed."""
        self._is_needed = False
        return self

    async def mark_known_entity_id(self, entity_id: EntityId) -> EntityProgressReporter:
        """Mark the fact that we now know the entity id for the entity being processed."""
        self._entity_id = entity_id
        self._status.update(self.to_str_form())
        return self

    async def mark_known_name(self, name: str) -> EntityProgressReporter:
        """Mark the fact that we now know the entity name for the entity being processed."""
        self._entity_name = name
        self._status.update(self.to_str_form())
        return self

    async def mark_local_change(self) -> EntityProgressReporter:
        """Mark the fact that the local change has succeeded."""
        self._local_change_status = MarkProgressStatus.OK
        self._status.update(self.to_str_form())
        return self

    async def mark_remote_change(
        self,
        success: MarkProgressStatus = MarkProgressStatus.OK,
    ) -> EntityProgressReporter:
        """Mark the fact that the remote change has completed."""
        self._remote_change_status = success
        self._status.update(self.to_str_form())
        return self

    async def mark_other_progress(
        self,
        progress: str,
        success: MarkProgressStatus = MarkProgressStatus.OK,
    ) -> EntityProgressReporter:
        """Mark some other type of progress."""
        self._progresses.append((progress, success))
        self._status.update(self.to_str_form())
        return self

    def to_str_form(self) -> Text:
        """Prepare the intermediary string form for this one."""
        text = Text(f"Working on {self._action_type} {self._entity_type}")
        if self._entity_id is not None:
            text.append(" ")
            text.append(entity_id_to_rich_text(self._entity_id))
        if self._entity_name is not None:
            text.append(" ")
            text.append(self._entity_name)
        if self._local_change_status is not None:
            if self._local_change_status == MarkProgressStatus.PROGRESS:
                text.append(" 🧭 local")
            elif self._local_change_status == MarkProgressStatus.OK:
                text.append(" ✅ local")
            elif self._local_change_status == MarkProgressStatus.FAILED:
                text.append(" ⭕ local")
            else:
                text.append(" ☑️  local")
        if self._remote_change_status is not None:
            if self._remote_change_status == MarkProgressStatus.PROGRESS:
                text.append(" 🧭 remote")
            elif self._remote_change_status == MarkProgressStatus.OK:
                text.append(" ✅ remote")
            elif self._remote_change_status == MarkProgressStatus.FAILED:
                text.append(" ⭕ remote")
            else:
                text.append(" ☑️ local")
        for progress, progress_status in self._progresses:
            if progress_status == MarkProgressStatus.PROGRESS:
                text.append(f" 🧭 {progress}")
            elif progress_status == MarkProgressStatus.OK:
                text.append(f" ✅ {progress}")
            elif progress_status == MarkProgressStatus.FAILED:
                text.append(f" ⭕ {progress}")
            else:
                text.append(f" ☑️  {progress}")

        return text

    def to_final_str_form(self) -> Text:
        """Prepare the final string form for this one."""
        text = Text(
            self._print_indent * ".."
            + f"Done with {self._action_type} {self._entity_type}",
        )
        if self._entity_id is not None:
            text.append(" ")
            text.append(entity_id_to_rich_text(self._entity_id))
        if self._entity_name is not None:
            text.append(" ")
            text.append(self._entity_name)
        if self._local_change_status is not None:
            if self._local_change_status == MarkProgressStatus.PROGRESS:
                text.append(" 🧭 local")
            elif self._local_change_status == MarkProgressStatus.OK:
                text.append(" ✅ local")
            elif self._local_change_status == MarkProgressStatus.FAILED:
                text.append(" ⭕ local")
            else:
                text.append(" ☑️  local")
        if self._remote_change_status is not None:
            if self._remote_change_status == MarkProgressStatus.PROGRESS:
                text.append(" 🧭 remote")
            elif self._remote_change_status == MarkProgressStatus.OK:
                text.append(" ✅ remote")
            elif self._remote_change_status == MarkProgressStatus.FAILED:
                text.append(" ⭕ remote")
            else:
                text.append(" ☑️ remote")
        for progress, progress_status in self._progresses:
            if progress_status == MarkProgressStatus.PROGRESS:
                text.append(f" 🧭 {progress}")
            elif progress_status == MarkProgressStatus.OK:
                text.append(f" ✅ {progress}")
            elif progress_status == MarkProgressStatus.FAILED:
                text.append(f" ⭕ {progress}")
            else:
                text.append(f" ☑️  {progress}")
        return text

    @property
    def entity_id(self) -> EntityId:
        """The entity id if it was set."""
        if self._entity_id is None:
            raise Exception("Someone forgot to call `mark_known_entity_id`")
        return self._entity_id

    @property
    def is_needed(self) -> bool:
        """Whether this particular stream of updates was needed."""
        return self._is_needed


class RichConsoleContextProgressReporter(ContextProgressReporter):
    """A progress reporter based on a Rich console that outputs progress to the console."""

    _console: Final[Console]
    _status: Final[Status]
    _sections: Final[List[str]]
    _created_entities_stats: Final[DefaultDict[str, List[Tuple[str, EntityId]]]]
    _updated_entities_stats: Final[DefaultDict[str, int]]
    _archived_entities_stats: Final[DefaultDict[str, int]]
    _removed_entities_stats: Final[DefaultDict[str, int]]
    _print_indent: Final[int]
    _is_needed: bool

    def __init__(
        self,
        console: Console,
        status: Status,
        sections: List[str],
        created_entities_stats: DefaultDict[str, List[Tuple[str, EntityId]]],
        updated_entities_stats: DefaultDict[str, int],
        archived_entities_stats: DefaultDict[str, int],
        removed_entities_stats: DefaultDict[str, int],
        print_indent: int,
    ) -> None:
        """Constructor."""
        self._console = console
        self._status = status
        self._sections = sections
        self._created_entities_stats = created_entities_stats
        self._updated_entities_stats = updated_entities_stats
        self._archived_entities_stats = archived_entities_stats
        self._removed_entities_stats = removed_entities_stats
        self._print_indent = print_indent
        self._is_needed = False

    @asynccontextmanager
    async def section(self, title: str) -> AsyncIterator[None]:
        """Start a section or subsection."""
        self._sections.append(title)
        section_text = Text(self._sections[0])
        for section_title in self._sections[1:]:
            section_text.append(" // ")
            section_text.append(section_title)
        panel = Panel(section_text)
        self._console.print(panel)
        yield None
        self._sections.pop()

    @asynccontextmanager
    async def start_creating_entity(
        self,
        entity_type: str,
        entity_name: str,
    ) -> AsyncIterator[RichConsoleEntityProgressReporter]:
        """Report that a particular entity is being created."""
        entity_progress_reporter = RichConsoleEntityProgressReporter(
            self._console,
            self._status,
            entity_type,
            "creating",
            entity_name=entity_name,
            print_indent=self._print_indent,
        )

        self._status.update(entity_progress_reporter.to_str_form())
        await asyncio.sleep(0.01)  # Oh so ugly

        yield entity_progress_reporter

        if entity_progress_reporter.is_needed:
            self._created_entities_stats[entity_type].append(
                (entity_name, entity_progress_reporter.entity_id),
            )
            self._console.print(entity_progress_reporter.to_final_str_form())
            self._is_needed = True
        else:
            self._console.control(Control.move_to_column(0))

        self._status.update("Working on it ...")

    @asynccontextmanager
    async def start_updating_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> AsyncIterator[RichConsoleEntityProgressReporter]:
        """Report that a particular entity is being updated."""
        entity_progress_reporter = RichConsoleEntityProgressReporter(
            self._console,
            self._status,
            entity_type,
            "updating",
            entity_id=entity_id,
            entity_name=entity_name,
            print_indent=self._print_indent,
        )

        self._status.update(entity_progress_reporter.to_str_form())
        await asyncio.sleep(0.01)  # Oh so ugly

        yield entity_progress_reporter

        if entity_progress_reporter.is_needed:
            self._updated_entities_stats[entity_type] += 1
            self._console.print(entity_progress_reporter.to_final_str_form())
            self._is_needed = True
        else:
            self._console.control(Control.move_to_column(0))

        self._status.update("Working on it ...")

    @asynccontextmanager
    async def start_archiving_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> AsyncIterator[RichConsoleEntityProgressReporter]:
        """Report that a particular entity is being archived."""
        entity_progress_reporter = RichConsoleEntityProgressReporter(
            self._console,
            self._status,
            entity_type,
            "archiving",
            entity_id=entity_id,
            entity_name=entity_name,
            print_indent=self._print_indent,
        )

        self._status.update(entity_progress_reporter.to_str_form())
        await asyncio.sleep(0.01)  # Oh so ugly

        yield entity_progress_reporter

        if entity_progress_reporter.is_needed:
            self._archived_entities_stats[entity_type] += 1
            self._console.print(entity_progress_reporter.to_final_str_form())
            self._is_needed = True
        else:
            self._console.control(Control.move_to_column(0))

        self._status.update("Working on it ...")

    @asynccontextmanager
    async def start_removing_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> AsyncIterator[RichConsoleEntityProgressReporter]:
        """Report that a particular entity is being removed."""
        entity_progress_reporter = RichConsoleEntityProgressReporter(
            self._console,
            self._status,
            entity_type,
            "removing",
            entity_id=entity_id,
            entity_name=entity_name,
            print_indent=self._print_indent,
        )

        self._status.update(entity_progress_reporter.to_str_form())
        await asyncio.sleep(0.01)  # Oh so ugly

        yield entity_progress_reporter

        if entity_progress_reporter.is_needed:
            self._removed_entities_stats[entity_type] += 1
            self._console.print(entity_progress_reporter.to_final_str_form())
            self._is_needed = True
        else:
            self._console.control(Control.move_to_column(0))

        self._status.update("Working on it ...")

    @asynccontextmanager
    async def start_complex_entity_work(
        self,
        entity_type: str,
        entity_id: EntityId,
        entity_name: str,
    ) -> AsyncIterator[ContextProgressReporter]:
        """Create a progress reporter with some scoping to operate with subentities of a main entity."""
        subprogress_reporter = RichConsoleContextProgressReporter(
            console=self._console,
            status=self._status,
            sections=[],
            created_entities_stats=self._created_entities_stats,
            updated_entities_stats=self._updated_entities_stats,
            archived_entities_stats=self._archived_entities_stats,
            removed_entities_stats=self._removed_entities_stats,
            print_indent=self._print_indent + 1,
        )

        header_text = Text(f"Working on {entity_type} ")
        header_text.append(entity_id_to_rich_text(entity_id))
        header_text.append(" ")
        header_text.append(entity_name)

        self._console.print(header_text)
        await asyncio.sleep(0.01)  # Oh so ugly

        yield subprogress_reporter

        if subprogress_reporter.is_needed:
            self._is_needed = True
        else:
            self._status.stop()
            self._console.control(Control.move_to_column(0, -1))
            self._status.start()

        self._status.update("Working on it ...")

    def print_prologue(self, command_name: str, args: argparse.Namespace) -> None:
        """Print a prologue section."""
        command_text = Text(f"{command_name}")
        for arg, val in vars(args).items():
            if (
                arg == "subparser_name"
                or arg == "verbose_logging"
                or arg == "min_log_level"
                or arg == "just_show_version"
            ):
                continue  # Ugly, but not the worst thing!
            command_text.append(f" {arg}:{val}")
        command_text.stylize("green on blue bold underline")

        prologue_text = Text("Running command ").append(command_text)
        panel = Panel(prologue_text)
        self._console.print(panel)

    def print_epilogue(self) -> None:
        """Print a prologue section."""
        epilogue_tree = Tree("Results:", guide_style="bold bright_blue")
        if len(self._created_entities_stats):
            created_tree = epilogue_tree.add("Created:")
            for (
                entity_type,
                created_entity_list,
            ) in self._created_entities_stats.items():
                entity_count = len(created_entity_list)
                entity_type_tree = created_tree.add(
                    f"{entity_type} => {entity_count} in total",
                    guide_style="blue",
                )
                for entity_name, entity_id in created_entity_list:
                    created_entity_text = Text("")
                    created_entity_text.append(entity_id_to_rich_text(entity_id))
                    created_entity_text.append(" ")
                    created_entity_text.append(
                        entity_name_to_rich_text(EntityName.from_raw(entity_name)),
                    )
                    entity_type_tree.add(created_entity_text)
        if len(self._updated_entities_stats):
            updated_tree = epilogue_tree.add("Updated:")
            for entity_type, entity_count in self._updated_entities_stats.items():
                updated_tree.add(
                    f"{entity_type} => {entity_count} in total",
                    guide_style="blue",
                )
        if len(self._archived_entities_stats):
            archived_tree = epilogue_tree.add("Archived:")
            for entity_type, entity_count in self._archived_entities_stats.items():
                archived_tree.add(
                    f"{entity_type} => {entity_count} in total",
                    guide_style="blue",
                )
        if len(self._removed_entities_stats):
            removed_tree = epilogue_tree.add("Removed:")
            for entity_type, entity_count in self._removed_entities_stats.items():
                removed_tree.add(
                    f"{entity_type} => {entity_count} in total",
                    guide_style="blue",
                )

        results_panel = Panel(epilogue_tree)

        self._console.print(results_panel)

    @property
    def is_needed(self) -> bool:
        """Whether this whole section is actually needed for rendering."""
        return self._is_needed


class RichConsoleProgressReporterFactory(
    ProgressReporterFactory[AppLoggedInUseCaseContext]
):
    """A progress reporter factory that builds Rich progress reporters."""

    _console: Final[Console]
    _status: Final[Status]
    _stored_progress_reporter: Final[RichConsoleContextProgressReporter]
    _should_have_streaming_progress_report: bool

    def __init__(self) -> None:
        """Constructor."""
        self._console = Console()
        self._status = self._console.status("Working on it ...", spinner="bouncingBall")
        self._stored_progress_reporter = RichConsoleContextProgressReporter(
            console=self._console,
            status=self._status,
            sections=[],
            created_entities_stats=defaultdict(list),
            updated_entities_stats=defaultdict(lambda: 0),
            archived_entities_stats=defaultdict(lambda: 0),
            removed_entities_stats=defaultdict(lambda: 0),
            print_indent=0,
        )
        self._should_have_streaming_progress_report = True

    def new_reporter(
        self, context: AppLoggedInUseCaseContext
    ) -> ContextProgressReporter:
        """Create a new progress reporter."""
        if not self._should_have_streaming_progress_report:
            return NoOpContextProgressReporter()
        return self._stored_progress_reporter

    @contextmanager
    def envelope(
        self,
        should_have_streaming_progress_report: bool,
        command_name: str,
        args: argparse.Namespace,
    ) -> Iterator["RichConsoleProgressReporterFactory"]:
        """Evelope execution of this with nice graphics."""
        self._should_have_streaming_progress_report = (
            should_have_streaming_progress_report
        )
        try:
            if should_have_streaming_progress_report:
                self._status.start()
                self._stored_progress_reporter.print_prologue(command_name, args)
            yield self
            if should_have_streaming_progress_report:
                self._stored_progress_reporter.print_epilogue()
        finally:
            self._status.stop()


def entity_id_to_rich_text(entity_id: EntityId) -> Text:
    """Transform an entity id into text."""
    return Text(f"#{entity_id}", style="blue bold")


def inbox_task_status_to_rich_text(
    status: InboxTaskStatus,
    archived: bool = False,
) -> Text:
    """Transform an inbox task status into text."""
    if archived:
        if status == InboxTaskStatus.DONE:
            return Text("☑️ ")
        else:
            return Text("🔲")

    if status == InboxTaskStatus.NOT_STARTED:
        return Text("🧭")
    elif status == InboxTaskStatus.ACCEPTED:
        return Text("🔧")
    elif status == InboxTaskStatus.RECURRING:
        return Text("🔧")
    elif status == InboxTaskStatus.IN_PROGRESS:
        return Text("🚧")
    elif status == InboxTaskStatus.BLOCKED:
        return Text("⭕")
    elif status == InboxTaskStatus.NOT_DONE:
        return Text("⛔")
    elif status == InboxTaskStatus.DONE:
        return Text("✅")
    else:
        raise Exception("Serious error - unhandled enum case")


def big_plan_status_to_rich_text(status: BigPlanStatus, archived: bool) -> Text:
    """Transform a big plan status into text."""
    if archived:
        if status == BigPlanStatus.DONE:
            return Text("☑️ ")
        else:
            return Text("🔲")

    if status == BigPlanStatus.NOT_STARTED:
        return Text("🧭")
    elif status == BigPlanStatus.ACCEPTED:
        return Text("🔧")
    elif status == BigPlanStatus.IN_PROGRESS:
        return Text("🚧")
    elif status == BigPlanStatus.BLOCKED:
        return Text("⭕")
    elif status == BigPlanStatus.NOT_DONE:
        return Text("⛔")
    elif status == BigPlanStatus.DONE:
        return Text("✅")
    else:
        raise Exception("Serious error - unhandled enum case")


def actionable_date_to_rich_text(actionable_date: ADate) -> Text:
    """Transform an actionable date into text."""
    return Text("From ").append(
        ADate.to_user_date_str(actionable_date),
        style="underline",
    )


def start_date_to_rich_text(start_date: ADate) -> Text:
    """Transform a due date into text."""
    return Text("Start at ").append(
        ADate.to_user_date_str(start_date),
        style="underline",
    )


def end_date_to_rich_text(end_date: ADate) -> Text:
    """Transform a due date into text."""
    return Text("End at ").append(ADate.to_user_date_str(end_date), style="underline")


def due_date_to_rich_text(due_date: ADate) -> Text:
    """Transform a due date into text."""
    return Text("Due at ").append(ADate.to_user_date_str(due_date), style="underline")


def project_to_rich_text(project_name: ProjectName) -> Text:
    """Transform a project into text."""
    return Text("In Project ").append(str(project_name), style="underline")


def entity_name_to_rich_text(name: EntityName) -> Text:
    """Transform an entity name into text."""
    return Text(str(name), style="green underline")


def parent_entity_name_to_rich_text(parent_name: EntityName) -> Text:
    """Transform a parent entity name into text."""
    return Text("From @").append(str(parent_name), style="underline italic")


def period_to_rich_text(period: RecurringTaskPeriod) -> Text:
    """Transform a period into text."""
    return Text(period.to_nice(), style="underline")


def eisen_to_rich_text(eisen: Eisen) -> Text:
    """Transform an eisenhower value into text."""
    return Text(eisen.to_nice(), style="underline green")


def person_relationship_to_rich_text(person_relationship: PersonRelationship) -> Text:
    """Transform person relationship into text."""
    return Text(person_relationship.to_nice(), style="underline yellow")


def person_birthday_to_rich_text(birthday: PersonBirthday) -> Text:
    """Transform birthday into text."""
    return Text(f"Birthday on {birthday}", style="italic")


def metric_unit_to_rich_text(metric_unit: MetricUnit) -> Text:
    """Transform a metric unit into text."""
    return Text(metric_unit.to_nice(), style="italic")


def source_to_rich_text(source: InboxTaskSource) -> Text:
    """Transform a source value into text."""
    return Text(source.to_nice(), style="underline italic blue")


def difficulty_to_rich_text(difficulty: Difficulty) -> Text:
    """Transform a difficulty value into text."""
    return Text(difficulty.to_nice(), style="underline")


def skip_rule_to_rich_text(skip_rule: RecurringTaskSkipRule) -> Text:
    """Transform a skip rule to text."""
    return Text("Skip ").append(str(skip_rule))


def actionable_from_day_to_rich_text(
    actionable_from_day: RecurringTaskDueAtDay,
) -> Text:
    """Transform a actionable day to rich text."""
    return Text("From day ").append(str(actionable_from_day), style="underline")


def actionable_from_month_to_rich_text(
    actionable_from_month: RecurringTaskDueAtMonth,
) -> Text:
    """Transform a actionable month to rich text."""
    return Text("From month ").append(str(actionable_from_month), style="underline")


def due_at_time_to_rich_text(due_at_time: RecurringTaskDueAtTime) -> Text:
    """Transform a due time to rich text."""
    return Text("Due at ").append(str(due_at_time), style="underline")


def due_at_day_to_rich_text(due_at_day: RecurringTaskDueAtDay) -> Text:
    """Transform a due day to rich text."""
    return Text("Due at day ").append(str(due_at_day), style="underline")


def due_at_month_to_rich_text(due_at_month: RecurringTaskDueAtMonth) -> Text:
    """Transform a due month to rich text."""
    return Text("Due at month ").append(str(due_at_month), style="underline")


def inbox_task_summary_to_rich_text(inbox_task: InboxTask) -> Text:
    """Transform a full inbox task to rich text."""
    text = inbox_task_status_to_rich_text(inbox_task.status, inbox_task.archived)
    text.append(" ")
    text.append(entity_id_to_rich_text(inbox_task.ref_id))
    text.append(f" {inbox_task.name}")

    if inbox_task.actionable_date is not None:
        text.append(" ")
        text.append(actionable_date_to_rich_text(inbox_task.actionable_date))

    if inbox_task.due_date is not None:
        text.append(" ")
        text.append(due_date_to_rich_text(inbox_task.due_date))

    if inbox_task.archived:
        text.stylize("grey62")

    return text


def slack_user_name_to_rich_text(user: SlackUserName) -> Text:
    """Transform a slack user name to rich text."""
    return Text("@").append(str(user), style="bold on white underline")


def slack_channel_name_to_rich_text(channel: SlackChannelName) -> Text:
    """Transform a slack channel name to rich text."""
    return Text("in #").append(str(channel), style="italic green")


def slack_task_message_to_rich_text(message: str) -> Text:
    """Transform a message to rich text."""
    text = Text("")
    message = " ".join(m.strip() for m in message.strip().split("\n"))
    if len(message) <= 100:
        text.append(" said 💬 ")
        text.append(message)
    else:
        text.append(" said 💬 ")
        text.append(message[0:98])
        text.append("...")
    return text


def email_user_name_to_rich_text(user: EmailUserName) -> Text:
    """Transform an email name to rich text."""
    return Text(str(user), style="bold on white underline")


def email_address_to_rich_text(address: EmailAddress) -> Text:
    """Transform an email address to rich text."""
    return Text(str(address), style="underline")


def email_task_subject_to_rich_text(subject: str) -> Text:
    """Transform a subject to rich text."""
    text = Text("")
    subject = " ".join(m.strip() for m in subject.strip().split("\n"))
    if len(subject) <= 100:
        text.append(" on 💬 ")
        text.append(subject)
    else:
        text.append(" on 💬 ")
        text.append(subject[0:98])
        text.append("...")
    return text


def timezone_to_rich_text(timezone: Timezone) -> Text:
    """Transform a timezone to rich text."""
    return Text(str(timezone), style="bold")
