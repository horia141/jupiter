"""Basic model types and validators for them."""
import datetime
import enum
import re
from typing import Dict, Iterable, Optional, NewType, Final, FrozenSet, Tuple, Pattern, Union, cast
from urllib.parse import urlparse

import pendulum
import pendulum.parsing.exceptions
from notion.collection import NotionDate
from pendulum.tz.timezone import Timezone, UTC
from pendulum.tz.zoneinfo.exceptions import InvalidTimezone

from utils.global_properties import GlobalProperties


class ModelValidationError(Exception):
    """An exception raised when validating some model type."""


@enum.unique
class SyncTarget(enum.Enum):
    """What exactly to sync."""
    STRUCTURE = "structure"
    WORKSPACE = "workspace"
    VACATIONS = "vacations"
    PROJECTS = "projects"
    INBOX_TASKS = "inbox-tasks"
    RECURRING_TASKS = "recurring-tasks"
    BIG_PLANS = "big-plans"
    SMART_LISTS = "smart-lists"
    METRICS = "metrics"


@enum.unique
class SyncPrefer(enum.Enum):
    """The source of data to prefer for a sync operation."""
    LOCAL = "local"
    NOTION = "notion"


Timestamp = NewType("Timestamp", pendulum.DateTime)  # type: ignore


ADate = Union[pendulum.Date, pendulum.DateTime]


EntityId = NewType("EntityId", str)


EntityName = NewType("EntityName", str)


Tag = NewType("Tag", str)


WorkspaceSpaceId = NewType("WorkspaceSpaceId", str)


WorkspaceToken = NewType("WorkspaceToken", str)


ProjectKey = NewType("ProjectKey", str)


SmartListKey = NewType("SmartListKey", str)


MetricKey = NewType("MetricKey", str)


@enum.unique
class Eisen(enum.Enum):
    """The Eisenhower status of a particular task."""
    IMPORTANT = "important"
    URGENT = "urgent"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return str(self.value).capitalize()


@enum.unique
class Difficulty(enum.Enum):
    """The difficulty of a particular task."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return str(self.value).capitalize()


@enum.unique
class InboxTaskStatus(enum.Enum):
    """The status of an inbox task."""
    # Created
    NOT_STARTED = "not-started"
    # Accepted
    ACCEPTED = "accepted"
    RECURRING = "recurring"
    # Working
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    # Completed
    NOT_DONE = "not-done"
    DONE = "done"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return " ".join(s.capitalize() for s in str(self.value).split("-"))

    @property
    def is_accepted(self) -> bool:
        """Whether the status means work has been accepted on the inbox task."""
        return self in (InboxTaskStatus.ACCEPTED, InboxTaskStatus.RECURRING)

    @property
    def is_accepted_or_more(self) -> bool:
        """Whether the status means work has been accepted, or is ongoing, or is completed."""
        return self.is_accepted or self.is_working or self.is_completed

    @property
    def is_working(self) -> bool:
        """Whether the status means work is ongoing for the inbox task."""
        return self in (InboxTaskStatus.IN_PROGRESS, InboxTaskStatus.BLOCKED)

    @property
    def is_working_or_more(self) -> bool:
        """Whether the status means work is ongoing, or is completed."""
        return self.is_working or self.is_completed

    @property
    def is_completed(self) -> bool:
        """Whether the status means work is completed on the inbox task."""
        return self in (InboxTaskStatus.NOT_DONE, InboxTaskStatus.DONE)


@enum.unique
class InboxTaskSource(enum.Enum):
    """The origin of an inbox task."""
    USER = "user"
    BIG_PLAN = "big-plan"
    RECURRING_TASK = "recurring-task"
    METRIC = "metric"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return " ".join(s.capitalize() for s in str(self.value).split("-"))

    @property
    def allow_user_changes(self) -> bool:
        """Allow user changes for an inbox task."""
        return self in (InboxTaskSource.USER, InboxTaskSource.BIG_PLAN)


@enum.unique
class RecurringTaskPeriod(enum.Enum):
    """A period for a particular task."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return str(self.value).capitalize()


@enum.unique
class RecurringTaskType(enum.Enum):
    """The type of recurring class."""
    CHORE = "chore"
    HABIT = "habit"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return str(self.value).capitalize()


@enum.unique
class BigPlanStatus(enum.Enum):
    """The status of a big plan."""
    # Created
    NOT_STARTED = "not-started"
    # Accepted
    ACCEPTED = "accepted"
    # Working
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    # Completed
    NOT_DONE = "not-done"
    DONE = "done"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return " ".join(s.capitalize() for s in str(self.value).split("-"))

    @property
    def is_accepted(self) -> bool:
        """Whether the status means work has been accepted on the inbox task."""
        return self == BigPlanStatus.ACCEPTED

    @property
    def is_accepted_or_more(self) -> bool:
        """Whether the status means work has been accepted, or is ongoing, or is completed."""
        return self.is_accepted or self.is_working or self.is_completed

    @property
    def is_working(self) -> bool:
        """Whether the status means work is ongoing for the inbox task."""
        return self in (BigPlanStatus.IN_PROGRESS, BigPlanStatus.BLOCKED)

    @property
    def is_working_or_more(self) -> bool:
        """Whether the status means work is ongoing, or is completed."""
        return self.is_working or self.is_completed

    @property
    def is_completed(self) -> bool:
        """Whether the status means work is completed on the inbox task."""
        return self in (BigPlanStatus.NOT_DONE, BigPlanStatus.DONE)


@enum.unique
class MetricUnit(enum.Enum):
    """The unit for a metric."""
    COUNT = "count"
    MONETARY_AMOUNT = "money"
    WEIGHT = "weight"

    def for_notion(self) -> str:
        """A prettier version of the value for Notion."""
        return str(self.value).capitalize()


class BasicValidator:
    """A validator class for various basic model types."""

    _sync_target_values: Final[FrozenSet[str]] = frozenset(st.value for st in SyncTarget)
    _sync_prefer_values: Final[FrozenSet[str]] = frozenset(sp.value for sp in SyncPrefer)
    _entity_id_re: Final[Pattern[str]] = re.compile(r"^\d+$")
    _entity_name_re: Final[Pattern[str]] = re.compile(r"^.+$")
    _workspace_space_id_re: Final[Pattern[str]] = re.compile(r"^[0-9a-z-]{36}$")
    _workspace_token_re: Final[Pattern[str]] = re.compile(r"^[0-9a-f]+$")
    _project_key_re: Final[Pattern[str]] = re.compile(r"^[a-z0-9]([a-z0-9]*-?)*$")
    _smart_list_key_re: Final[Pattern[str]] = re.compile(r"^[a-z0-9]([a-z0-9]*-?)*$")
    _metric_key_re: Final[Pattern[str]] = re.compile(r"^[a-z0-9]([a-z0-9]*-?)*$")
    _eisen_values: Final[FrozenSet[str]] = frozenset(e.value for e in Eisen)
    _difficulty_values: Final[FrozenSet[str]] = frozenset(d.value for d in Difficulty)
    _inbox_task_status_values: Final[FrozenSet[str]] = frozenset(its.value for its in InboxTaskStatus)
    _inbox_task_source_values: Final[FrozenSet[str]] = frozenset(its.value for its in InboxTaskSource)
    _recurring_task_period_values: Final[FrozenSet[str]] = frozenset(rtp.value for rtp in RecurringTaskPeriod)
    _recurring_task_type_values: Final[FrozenSet[str]] = frozenset(rtt.value for rtt in RecurringTaskType)
    _recurring_task_due_at_time_re: Final[Pattern[str]] = re.compile(r"^[0-9][0-9]:[0-9][0-9]$")
    _recurring_task_due_at_day_bounds: Final[Dict[RecurringTaskPeriod, Tuple[int, int]]] = {
        RecurringTaskPeriod.DAILY: (0, 0),
        RecurringTaskPeriod.WEEKLY: (1, 6),
        RecurringTaskPeriod.MONTHLY: (1, 31),
        RecurringTaskPeriod.QUARTERLY: (1, 31),
        RecurringTaskPeriod.YEARLY: (1, 31)
    }
    _recurring_task_due_at_month_bounds: Final[Dict[RecurringTaskPeriod, Tuple[int, int]]] = {
        RecurringTaskPeriod.DAILY: (0, 0),
        RecurringTaskPeriod.WEEKLY: (0, 0),
        RecurringTaskPeriod.MONTHLY: (0, 0),
        RecurringTaskPeriod.QUARTERLY: (1, 3),
        RecurringTaskPeriod.YEARLY: (1, 12)
    }
    _big_plan_status_values: Final[FrozenSet[str]] = frozenset(bps.value for bps in BigPlanStatus)
    _tag_re: Final[Pattern[str]] = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9]*-?)*$")
    _metric_unit_values: Final[FrozenSet[str]] = frozenset(mu.value for mu in MetricUnit)

    _global_properties: Final[GlobalProperties]

    def __init__(self, global_properties: GlobalProperties) -> None:
        """Constructor."""
        self._global_properties = global_properties

    def sync_target_validate_and_clean(self, sync_target_raw: Optional[str]) -> SyncTarget:
        """Validate and clean the big plan status."""
        if not sync_target_raw:
            raise ModelValidationError("Expected sync target to be non-null")

        sync_target_str: str = sync_target_raw.strip().lower()

        if sync_target_str not in self._sync_target_values:
            raise ModelValidationError(
                f"Expected sync prefer '{sync_target_raw}' to be one of '{','.join(self._sync_target_values)}'")

        return SyncTarget(sync_target_str)

    @staticmethod
    def sync_target_values() -> Iterable[str]:
        """The possible values for sync targets."""
        return BasicValidator._sync_target_values

    def sync_prefer_validate_and_clean(self, sync_prefer_raw: Optional[str]) -> SyncPrefer:
        """Validate and clean the big plan status."""
        if not sync_prefer_raw:
            raise ModelValidationError("Expected sync prefer to be non-null")

        sync_prefer_str: str = sync_prefer_raw.strip().lower()

        if sync_prefer_str not in self._sync_prefer_values:
            raise ModelValidationError(
                f"Expected sync prefer '{sync_prefer_raw}' to be one of '{','.join(self._sync_prefer_values)}'")

        return SyncPrefer(sync_prefer_str)

    @staticmethod
    def sync_prefer_values() -> Iterable[str]:
        """The possible values for sync prefer."""
        return BasicValidator._sync_prefer_values

    @staticmethod
    def entity_id_validate_and_clean(entity_id_raw: Optional[str]) -> EntityId:
        """Validate and clean an entity id."""
        if not entity_id_raw:
            raise ModelValidationError("Expected entity id to be non-null")

        entity_id: str = entity_id_raw.strip()

        if len(entity_id) == 0:
            raise ModelValidationError("Expected entity id to be non-empty")

        if not BasicValidator._entity_id_re.match(entity_id):
            raise ModelValidationError(
                f"Expected entity id '{entity_id_raw}' to match '{BasicValidator._entity_id_re.pattern}")

        return EntityId(entity_id)

    @staticmethod
    def entity_name_validate_and_clean(entity_name_raw: Optional[str]) -> EntityName:
        """Validate and clean an entity name."""
        if not entity_name_raw:
            raise ModelValidationError("Expected entity name to be non-null")

        entity_name: str = " ".join(word for word in entity_name_raw.strip().split(" ") if len(word) > 0)

        if len(entity_name) == 0:
            raise ModelValidationError("Expected entity name to be non-empty")

        if not BasicValidator._entity_name_re.match(entity_name):
            raise ModelValidationError(
                f"Expected entity id '{entity_name_raw}' to match '{BasicValidator._entity_name_re.pattern}")

        return EntityName(entity_name)

    def workspace_space_id_validate_and_clean(self, workspace_space_id_raw: Optional[str]) -> WorkspaceSpaceId:
        """Validate and clean a workspace space id."""
        if not workspace_space_id_raw:
            raise ModelValidationError("Expected workspace space id to be non-null")

        workspace_space_id: str = workspace_space_id_raw.strip().lower()

        if len(workspace_space_id) == 0:
            raise ModelValidationError("Expected workspace space id to be non-empty")

        if not self._workspace_space_id_re.match(workspace_space_id):
            raise ModelValidationError(
                f"Expected workspace space id '{workspace_space_id}' to match '{self._workspace_space_id_re.pattern}")

        return WorkspaceSpaceId(workspace_space_id)

    def workspace_token_validate_and_clean(self, workspace_token_raw: Optional[str]) -> WorkspaceToken:
        """Validate and clean a workspace token."""
        if not workspace_token_raw:
            raise ModelValidationError("Expected workspace token to be non-null")

        workspace_token: str = workspace_token_raw.strip().lower()

        if len(workspace_token) == 0:
            raise ModelValidationError("Expected workspace token to be non-empty")

        if not self._workspace_token_re.match(workspace_token):
            raise ModelValidationError(
                f"Expected workspace token '{workspace_token}' to match '{self._workspace_token_re.pattern}")

        return WorkspaceToken(workspace_token)

    def project_key_validate_and_clean(self, project_key_raw: Optional[str]) -> ProjectKey:
        """Validate and clean a project key."""
        if not project_key_raw:
            raise ModelValidationError("Expected project key to be non-null")

        project_key_str: str = project_key_raw.strip().lower()

        if len(project_key_str) == 0:
            raise ModelValidationError("Expected project key to be non-empty")

        if not self._project_key_re.match(project_key_str):
            raise ModelValidationError(
                f"Expected project key '{project_key_raw}' to match '{self._project_key_re.pattern}'")

        return ProjectKey(project_key_str)

    def smart_list_key_validate_and_clean(self, smart_list_key_raw: Optional[str]) -> SmartListKey:
        """Validate and clean a smart list key."""
        if not smart_list_key_raw:
            raise ModelValidationError("Expected smart list key to be non-null")

        smart_list_key_str: str = smart_list_key_raw.strip().lower()

        if len(smart_list_key_str) == 0:
            raise ModelValidationError("Expected smart list key to be non-empty")

        if not self._smart_list_key_re.match(smart_list_key_str):
            raise ModelValidationError(
                f"Expected smart list key '{smart_list_key_raw}' to match '{self._smart_list_key_re.pattern}'")

        return SmartListKey(smart_list_key_str)

    @staticmethod
    def metric_key_validate_and_clean(metric_key_raw: Optional[str]) -> MetricKey:
        """Validate and clean a metric."""
        if not metric_key_raw:
            raise ModelValidationError("Expected metric key key to be non-null")

        metric_key_str: str = metric_key_raw.strip().lower()

        if len(metric_key_str) == 0:
            raise ModelValidationError("Expected metric key to be non-empty")

        if not BasicValidator._metric_key_re.match(metric_key_str):
            raise ModelValidationError(
                f"Expected metric key '{metric_key_raw}' to match '{BasicValidator._metric_key_re.pattern}'")

        return MetricKey(metric_key_str)

    def timestamp_validate_and_clean(self, timestamp_raw: Optional[str]) -> Timestamp:
        """Validate and clean an optional timestamp."""
        if not timestamp_raw:
            raise ModelValidationError("Expected timestamp to be non-null")

        try:
            timestamp = pendulum.parse(timestamp_raw, tz=self._global_properties.timezone, exact=True)

            if isinstance(timestamp, pendulum.DateTime):
                timestamp = timestamp.in_timezone(UTC)
            elif isinstance(timestamp, pendulum.Date):
                timestamp = pendulum.DateTime(timestamp.year, timestamp.month, timestamp.day, tzinfo=UTC)
            else:
                raise ModelValidationError(f"Expected datetime '{timestamp_raw}' to be in a proper datetime format")

            return Timestamp(timestamp)
        except pendulum.parsing.exceptions.ParserError as error:
            raise ModelValidationError(f"Expected datetime '{timestamp_raw}' to be in a proper format") from error

    @staticmethod
    def timestamp_from_str(timestamp_raw: str) -> Timestamp:
        """Parse a timestamp from a string."""
        timestamp = pendulum.parse(timestamp_raw, tz=UTC, exact=True)
        if not isinstance(timestamp, pendulum.DateTime):
            raise ModelValidationError(f"Expected timestamp '{timestamp_raw}' to be in a proper timestamp format")
        return Timestamp(timestamp)

    @staticmethod
    def timestamp_to_str(timestamp: Timestamp) -> str:
        """Transform a timestamp to a string."""
        return cast(str, timestamp.to_datetime_string())

    def adate_validate_and_clean(self, datetime_raw: Optional[str]) -> ADate:
        """Validate and clean an optional datetime."""
        if not datetime_raw:
            raise ModelValidationError("Expected datetime to be non-null")

        try:
            adate = pendulum.parse(datetime_raw, tz=self._global_properties.timezone, exact=True)

            if isinstance(adate, pendulum.DateTime):
                adate = adate.in_timezone(UTC)
            elif isinstance(adate, pendulum.Date):
                pass
            else:
                raise ModelValidationError(f"Expected datetime '{datetime_raw}' to be in a proper datetime format")

            return adate
        except pendulum.parsing.exceptions.ParserError as error:
            raise ModelValidationError(f"Expected datetime '{datetime_raw}' to be in a proper format") from error

    @staticmethod
    def adate_from_str(adata_raw: str) -> ADate:
        """Parse a date from string."""
        return pendulum.parse(adata_raw.replace(" 00:00:00", ""), tz=UTC, exact=True)

    @staticmethod
    def adate_to_str(adate: ADate) -> str:
        """Transform a date to string."""
        if isinstance(adate, pendulum.DateTime):
            return cast(str, adate.to_datetime_string())
        else:
            return cast(str, adate.to_date_string())

    def adate_from_notion(self, adate_raw: NotionDate) -> ADate:
        """Parse a date from a Notion representation."""
        adate_raw = pendulum.parse(
            str(adate_raw.start), exact=True, tz=self._global_properties.timezone)
        if isinstance(adate_raw, pendulum.DateTime):
            return adate_raw.in_timezone(UTC)
        else:
            return adate_raw

    def adate_to_notion(self, adate: ADate) -> NotionDate:
        """Transform a date to a Notion representation."""
        if isinstance(adate, pendulum.DateTime):
            return NotionDate(adate, timezone=self._global_properties.timezone.name)
        else:
            return NotionDate(adate)

    @staticmethod
    def timestamp_from_notion_timestamp(timestamp_raw: datetime.datetime) -> Timestamp:
        """Parse a timestamp from a Notion representation."""
        return Timestamp(pendulum.instance(timestamp_raw).in_timezone(UTC))

    def timestamp_to_notion_timestamp(self, timestamp: Timestamp) -> datetime.datetime:
        """Transform a timestamp to a Notion representation."""
        return cast(Timestamp, timestamp.in_timezone(self._global_properties.timezone))

    @staticmethod
    def timestamp_from_db_timestamp(timestamp_raw: datetime.datetime) -> Timestamp:
        """Parse a timestamp from a Notion representation."""
        return Timestamp(pendulum.instance(timestamp_raw).in_timezone(UTC))

    @staticmethod
    def timestamp_to_db_timestamp(timestamp: Timestamp) -> datetime.datetime:
        """Transform a timestamp to a Notion representation."""
        return timestamp

    def adate_to_user(self, adate: Optional[ADate]) -> str:
        """Transform a date to something meaningful to a user."""
        if not adate:
            return ""
        if isinstance(adate, pendulum.DateTime):
            return cast(str, adate.in_timezone(self._global_properties.timezone).to_datetime_string())
        else:
            return cast(str, adate.to_date_string())

    @staticmethod
    def eisen_validate_and_clean(eisen_raw: Optional[str]) -> Eisen:
        """Validate and clean the Eisenhower status."""
        if not eisen_raw:
            raise ModelValidationError("Expected Eisenhower status to be non-null")

        eisen_str: str = eisen_raw.strip().lower()

        if eisen_str not in BasicValidator._eisen_values:
            raise ModelValidationError(
                f"Expected Eisenhower status '{eisen_raw}' to be one of '{','.join(BasicValidator._eisen_values)}'")

        return Eisen(eisen_str)

    @staticmethod
    def eisen_values() -> Iterable[str]:
        """The possible values for Eisenhower statues."""
        return BasicValidator._eisen_values

    @staticmethod
    def difficulty_validate_and_clean(difficulty_raw: Optional[str]) -> Difficulty:
        """Validate and clean the difficulty."""
        if not difficulty_raw:
            raise ModelValidationError("Expected difficulty to be non-null")

        difficulty_str: str = difficulty_raw.strip().lower()

        if difficulty_str not in BasicValidator._difficulty_values:
            raise ModelValidationError(
                f"Expected difficulty '{difficulty_raw}' to be one of '{','.join(BasicValidator._difficulty_values)}'")

        return Difficulty(difficulty_str)

    @staticmethod
    def difficulty_values() -> Iterable[str]:
        """The possible values for difficulty."""
        return BasicValidator._difficulty_values

    def inbox_task_status_validate_and_clean(self, inbox_task_status_raw: Optional[str]) -> InboxTaskStatus:
        """Validate and clean the big plan status."""
        if not inbox_task_status_raw:
            raise ModelValidationError("Expected inbox task status to be non-null")

        inbox_task_status_str: str = '-'.join(inbox_task_status_raw.strip().lower().split(' '))

        if inbox_task_status_str not in self._inbox_task_status_values:
            raise ModelValidationError(
                f"Expected inbox task status '{inbox_task_status_raw}' to be " +
                f"one of '{','.join(self._inbox_task_status_values)}'")

        return InboxTaskStatus(inbox_task_status_str)

    @staticmethod
    def inbox_task_status_values() -> Iterable[str]:
        """The possible values for inbox task statues."""
        return BasicValidator._inbox_task_status_values

    @staticmethod
    def inbox_task_source_validate_and_clean(inbox_task_source_raw: Optional[str]) -> InboxTaskSource:
        """Validate and clean the big plan source."""
        if not inbox_task_source_raw:
            raise ModelValidationError("Expected inbox task source to be non-null")

        inbox_task_source_str: str = '-'.join(inbox_task_source_raw.strip().lower().split(' '))

        if inbox_task_source_str not in BasicValidator._inbox_task_source_values:
            raise ModelValidationError(
                f"Expected inbox task source '{inbox_task_source_raw}' to be " +
                f"one of '{','.join(BasicValidator._inbox_task_source_values)}'")

        return InboxTaskSource(inbox_task_source_str)

    @staticmethod
    def inbox_task_source_values() -> Iterable[str]:
        """The possible values for inbox task statues."""
        return BasicValidator._inbox_task_source_values

    @staticmethod
    def recurring_task_period_validate_and_clean(recurring_task_period_raw: Optional[str]) -> RecurringTaskPeriod:
        """Validate and clean the recurring task period."""
        if not recurring_task_period_raw:
            raise ModelValidationError("Expected recurring task period to be non-null")

        recurring_task_period_str: str = recurring_task_period_raw.strip().lower()

        if recurring_task_period_str not in BasicValidator._recurring_task_period_values:
            raise ModelValidationError(
                f"Expected recurring task period '{recurring_task_period_raw}' to be " +
                f"one of '{','.join(BasicValidator._recurring_task_period_values)}'")

        return RecurringTaskPeriod(recurring_task_period_str)

    @staticmethod
    def recurring_task_period_values() -> Iterable[str]:
        """The possible values for recurring task periods."""
        return BasicValidator._recurring_task_period_values

    def recurring_task_type_validate_and_clean(self, recurring_task_type_raw: Optional[str]) -> RecurringTaskType:
        """Validate and clean the recurring task type."""
        if not recurring_task_type_raw:
            raise ModelValidationError("Expected big plan status to be non-null")

        recurring_task_type_str: str = recurring_task_type_raw.strip().lower()

        if recurring_task_type_str not in self._recurring_task_type_values:
            raise ModelValidationError(
                f"Expected recurring task type '{recurring_task_type_raw}' to be " +
                f"one of '{','.join(self._recurring_task_type_values)}'")

        return RecurringTaskType(recurring_task_type_str)

    @staticmethod
    def recurring_task_type_values() -> Iterable[str]:
        """The possible values for recurring task types."""
        return BasicValidator._recurring_task_type_values

    def recurring_task_due_at_time_validate_and_clean(self, recurring_task_due_at_time_raw: Optional[str]) -> str:
        """Validate and clean the due at time info."""
        if not recurring_task_due_at_time_raw:
            raise ModelValidationError("Expected the due time info to be non-null")

        recurring_task_due_at_time_str: str = recurring_task_due_at_time_raw.strip().lower()

        if len(recurring_task_due_at_time_str) == 0:
            raise ModelValidationError("Expected due time info to be non-empty")

        if not self._recurring_task_due_at_time_re.match(recurring_task_due_at_time_str):
            raise ModelValidationError(
                f"Expected due time info '{recurring_task_due_at_time_raw}' to " +
                f"match '{self._recurring_task_due_at_time_re.pattern}'")

        return recurring_task_due_at_time_str

    def recurring_task_due_at_day_validate_and_clean(
            self, period: RecurringTaskPeriod, recurring_task_due_at_day_raw: Optional[int]) -> int:
        """Validate and clean the recurring task due at day info."""
        if not recurring_task_due_at_day_raw:
            raise ModelValidationError("Expected the due day info to be non-null")

        bounds = self._recurring_task_due_at_day_bounds[period]

        if recurring_task_due_at_day_raw < bounds[0] or recurring_task_due_at_day_raw > bounds[1]:
            raise ModelValidationError(
                f"Expected the due day info for {period} period to be a value between {bounds[0]} and {bounds[1]}")

        return recurring_task_due_at_day_raw

    def recurring_task_due_at_month_validate_and_clean(
            self, period: RecurringTaskPeriod, recurring_task_due_at_month_raw: Optional[int]) -> int:
        """Validate and clean the recurring task due at day info."""
        if not recurring_task_due_at_month_raw:
            raise ModelValidationError("Expected the due month info to be non-null")

        bounds = self._recurring_task_due_at_month_bounds[period]

        if recurring_task_due_at_month_raw < bounds[0] or recurring_task_due_at_month_raw > bounds[1]:
            raise ModelValidationError(
                f"Expected the due month info for {period} period to be a value between {bounds[0]} and {bounds[1]}")

        return recurring_task_due_at_month_raw

    @staticmethod
    def recurring_task_skip_rule_validate_and_clean(recurring_task_skip_rule_raw: Optional[str]) -> str:
        """Validate and clean the recurring task skip rule."""
        if not recurring_task_skip_rule_raw:
            raise ModelValidationError("Expected the skip rule info to be non-null")

        return recurring_task_skip_rule_raw.strip().lower()

    def big_plan_status_validate_and_clean(self, big_plan_status_raw: Optional[str]) -> BigPlanStatus:
        """Validate and clean the big plan status."""
        if not big_plan_status_raw:
            raise ModelValidationError("Expected big plan status to be non-null")

        big_plan_status_str: str = '-'.join(big_plan_status_raw.strip().lower().split(' '))

        if big_plan_status_str not in self._big_plan_status_values:
            raise ModelValidationError(
                f"Expected big plan status '{big_plan_status_raw}' to be " +
                f"one of '{','.join(self._big_plan_status_values)}'")

        return BigPlanStatus(big_plan_status_str)

    @staticmethod
    def big_plan_status_values() -> Iterable[str]:
        """The possible values for big plan statues."""
        return BasicValidator._big_plan_status_values

    @staticmethod
    def metric_unit_validate_and_clean(metric_unit_raw: Optional[str]) -> MetricUnit:
        """Validate and clean the metric unit."""
        if not metric_unit_raw:
            raise ModelValidationError("Expected metric unit to be non-null")

        metric_unit_str: str = '-'.join(metric_unit_raw.strip().lower().split(' '))

        if metric_unit_str not in BasicValidator._metric_unit_values:
            raise ModelValidationError(
                f"Expected metric unit '{metric_unit_raw}' to be " +
                f"one of '{','.join(BasicValidator._metric_unit_values)}'")

        return MetricUnit(metric_unit_str)

    @staticmethod
    def metric_unit_values() -> Iterable[str]:
        """The possible values for metric units."""
        return BasicValidator._metric_unit_values

    @staticmethod
    def timezone_validate_and_clean(timezone_raw: Optional[str]) -> Timezone:
        """Validate and clean a timezone."""
        if not timezone_raw:
            raise ModelValidationError("Expected timezone to be non-null")

        timezone_str: str = timezone_raw.strip()

        try:
            return pendulum.timezone(timezone_str)
        except InvalidTimezone as err:
            raise ModelValidationError(f"Invalid timezone '{timezone_raw}'") from err

    @staticmethod
    def url_validate_and_clean(url_raw: Optional[str]) -> str:
        """Validate and clean a url."""
        if not url_raw:
            raise ModelValidationError("Expected url to be non-null")

        url_str: str = url_raw.strip()

        try:
            return urlparse(url_str).geturl()
        except ValueError as err:
            raise ModelValidationError(f"Invalid URL '{url_raw}'") from err

    def tag_validate_and_clean(self, tag_raw: Optional[str]) -> Tag:
        """Validate and clean an tag."""
        if not tag_raw:
            raise ModelValidationError("Expected tag to be non-null")

        tag: str = " ".join(word for word in tag_raw.strip().split(" ") if len(word) > 0)

        if len(tag) == 0:
            raise ModelValidationError("Expected tag to be non-empty")

        if not self._tag_re.match(tag):
            raise ModelValidationError(
                f"Expected entity id '{tag_raw}' to match '{self._tag_re.pattern}'")

        return Tag(tag)
