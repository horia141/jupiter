"""Helpers for console rendering."""
import argparse
import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncIterator, DefaultDict, Final, Iterator, List, Tuple

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
from jupiter.core.domain.named_entity_tag import NamedEntityTag
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
from jupiter.core.framework.entity import BranchEntity, LeafEntity
from jupiter.core.framework.use_case import (
    ProgressReporter,
    ProgressReporterFactory,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseContext
from jupiter.core.utils.progress_reporter import NoOpProgressReporter
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.text import Text
from rich.tree import Tree


class RichConsoleProgressReporter(ProgressReporter):
    """A progress reporter based on a Rich console that outputs progress to the console."""

    _console: Final[Console]
    _status: Final[Status]
    _sections: Final[List[str]]
    _created_entities: Final[List[BranchEntity | LeafEntity]]
    _created_entities_stats: Final[
        DefaultDict[NamedEntityTag, List[Tuple[EntityName, EntityId]]]
    ]
    _updated_entities: Final[List[BranchEntity | LeafEntity]]
    _updated_entities_stats: Final[DefaultDict[NamedEntityTag, int]]
    _removed_entities: Final[List[BranchEntity | LeafEntity]]
    _removed_entities_stats: Final[DefaultDict[NamedEntityTag, int]]
    _print_indent: Final[int]

    def __init__(
        self,
        console: Console,
        status: Status,
        sections: List[str],
        created_entities: List[BranchEntity | LeafEntity],
        created_entities_stats: DefaultDict[
            NamedEntityTag, List[Tuple[EntityName, EntityId]]
        ],
        updated_entities: List[BranchEntity | LeafEntity],
        updated_entities_stats: DefaultDict[NamedEntityTag, int],
        removed_entities: List[BranchEntity | LeafEntity],
        removed_entities_stats: DefaultDict[NamedEntityTag, int],
        print_indent: int,
    ) -> None:
        """Constructor."""
        self._console = console
        self._status = status
        self._sections = sections
        self._created_entities = created_entities
        self._created_entities_stats = created_entities_stats
        self._updated_entities = updated_entities
        self._updated_entities_stats = updated_entities_stats
        self._removed_entities = removed_entities
        self._removed_entities_stats = removed_entities_stats
        self._print_indent = print_indent

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

    async def mark_created(self, entity: BranchEntity | LeafEntity) -> None:
        """Mark an entity as created."""
        self._created_entities.append(entity)
        self._created_entities_stats[NamedEntityTag.from_entity(entity)].append(
            (entity.name, entity.ref_id),
        )
        text = self._entity_to_str("creating", entity)
        self._status.update(text)
        await asyncio.sleep(0.01)
        self._console.print(text)
        self._status.update("Working on it ...")

    async def mark_updated(self, entity: BranchEntity | LeafEntity) -> None:
        """Mark an entity as created."""
        self._updated_entities.append(entity)
        self._updated_entities_stats[NamedEntityTag.from_entity(entity)] += 1
        text = self._entity_to_str("updating", entity)
        self._status.update(text)
        await asyncio.sleep(0.01)
        self._console.print(text)
        self._status.update("Working on it ...")

    async def mark_removed(self, entity: BranchEntity | LeafEntity) -> None:
        """Mark an entity as created."""
        self._removed_entities.append(entity)
        self._removed_entities_stats[NamedEntityTag.from_entity(entity)] += 1
        text = self._entity_to_str("removing", entity)
        self._status.update(text)
        await asyncio.sleep(0.01)
        self._console.print(text)
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
        """Print an epilogue section."""
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
                        entity_name_to_rich_text(entity_name),
                    )
                    entity_type_tree.add(created_entity_text)
        if len(self._updated_entities_stats):
            updated_tree = epilogue_tree.add("Updated:")
            for entity_type, entity_count in self._updated_entities_stats.items():
                updated_tree.add(
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
    def created_entities(self) -> List[BranchEntity | LeafEntity]:
        """Created entities."""
        return self._created_entities

    @property
    def updated_entities(self) -> List[BranchEntity | LeafEntity]:
        """Created entities."""
        return self._updated_entities

    @property
    def removed_entities(self) -> List[BranchEntity | LeafEntity]:
        """Created entities."""
        return self._removed_entities

    def _entity_to_str(
        self, action_type: str, entity: BranchEntity | LeafEntity
    ) -> Text:
        """Prepare the final string form for this one."""
        text = Text(
            self._print_indent * ".."
            + f"✅ Done with {action_type} {NamedEntityTag.from_entity(entity)}",
        )

        text.append(" ")
        text.append(entity_id_to_rich_text(entity.ref_id))
        text.append(" ")
        text.append(entity_name_to_rich_text(entity.name))

        return text


class RichConsoleProgressReporterFactory(
    ProgressReporterFactory[AppLoggedInUseCaseContext]
):
    """A progress reporter factory that builds Rich progress reporters."""

    _console: Final[Console]
    _status: Final[Status]
    _stored_progress_reporter: Final[RichConsoleProgressReporter]
    _should_have_streaming_progress_report: bool

    def __init__(self, console: Console) -> None:
        """Constructor."""
        self._console = console
        self._status = self._console.status("Working on it ...", spinner="bouncingBall")
        self._stored_progress_reporter = RichConsoleProgressReporter(
            console=self._console,
            status=self._status,
            sections=[],
            created_entities=[],
            created_entities_stats=defaultdict(list),
            updated_entities=[],
            updated_entities_stats=defaultdict(lambda: 0),
            removed_entities=[],
            removed_entities_stats=defaultdict(lambda: 0),
            print_indent=0,
        )
        self._should_have_streaming_progress_report = True

    def new_reporter(self, context: AppLoggedInUseCaseContext) -> ProgressReporter:
        """Create a new progress reporter."""
        if not self._should_have_streaming_progress_report:
            return NoOpProgressReporter()
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


def entity_tag_to_rich_text(entity_tag: NamedEntityTag) -> Text:
    """Transform a sync target into text."""
    return Text(entity_tag.value, style="blue italic")


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
