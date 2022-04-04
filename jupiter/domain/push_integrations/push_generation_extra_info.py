"""Extra information for how to generate an inbox task."""
import argparse
import shlex
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.domain.timezone import Timezone, UTC
from jupiter.framework.errors import InputValidationError
from jupiter.framework.value import Value


@dataclass(frozen=True)
class PushGenerationExtraInfo(Value):
    """Extra information for how to generate an inbox task."""

    timezone: Timezone
    name: Optional[InboxTaskName]
    status: Optional[InboxTaskStatus]
    eisen: Optional[Eisen]
    difficulty: Optional[Difficulty]
    actionable_date: Optional[ADate]
    due_date: Optional[ADate]

    @staticmethod
    def from_db(db_data: str) -> 'PushGenerationExtraInfo':
        """Parses a storage optimised form of the extra info."""
        return PushGenerationExtraInfo.from_raw_message_data(UTC, db_data)

    @staticmethod
    def from_raw_message_data(timezone: Timezone, raw_message_data: Optional[str]) -> 'PushGenerationExtraInfo':
        """Parses a user-supplied message and extracts the data to construct an inbox task."""
        if raw_message_data is None or raw_message_data.strip() == "":
            return PushGenerationExtraInfo(
                timezone=timezone, name=None, status=None, eisen=None, difficulty=None, actionable_date=None,
                due_date=None)

        parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
        parser.add_argument(
            "--name", dest="name", help="The name of the inbox task")
        parser.add_argument(
            "--status", dest="status", choices=InboxTaskStatus.all_values(),
            help="The initial status of the inbox task")
        parser.add_argument(
            "--eisen", dest="eisen", choices=Eisen.all_values(),
            help="The Eisenhower matrix values to use for task")
        parser.add_argument(
            "--difficulty", dest="difficulty", choices=Difficulty.all_values(),
            help="The difficulty to use for tasks")
        parser.add_argument(
            "--actionable-date", dest="actionable_date", help="The active date of the inbox task")
        parser.add_argument(
            "--due-date", dest="due_date", help="The due date of the big plan")

        try:
            message_as_options = shlex.split(raw_message_data)

            args = parser.parse_args(args=message_as_options)

            return PushGenerationExtraInfo(
                timezone=timezone,
                name=InboxTaskName.from_raw(args.name) if args.name else None,
                status=InboxTaskStatus.from_raw(args.status) if args.status else None,
                eisen=Eisen.from_raw(args.eisen) if args.eisen else None,
                difficulty=Difficulty.from_raw(args.difficulty) if args.difficulty else None,
                actionable_date=ADate.from_raw(timezone, args.actionable_date) if args.actionable_date else None,
                due_date=ADate.from_raw(timezone, args.due_date) if args.due_date else None)
        except ValueError as err:
            raise InputValidationError("Contents of extra info message is invalid") from err
        except SystemExit as err:
            raise InputValidationError("Contents of extra info message is invalid") from err

    def to_db(self) -> str:
        """Produce a string form of this."""
        return self._back_to_str(UTC)

    def to_raw_message_data(self) -> str:
        """Produce a string form of this."""
        return self._back_to_str(self.timezone)

    def _back_to_str(self, timezone: Timezone) -> str:
        string_pieces = []
        if self.name:
            string_pieces.append(f'--name="{self.name}"')
        if self.status:
            string_pieces.append(f'--status={self.status}')
        if self.eisen:
            string_pieces.append(f'--eisen={self.eisen}')
        if self.difficulty:
            string_pieces.append(f'--difficulty={self.difficulty}')
        if self.actionable_date:
            string_pieces.append(f'--actionable-date={ADate.to_user_str(self.timezone, self.actionable_date)}')
        if self.due_date:
            string_pieces.append(f'--due-date={ADate.to_user_str(timezone, self.due_date)}')
        return " ".join(string_pieces)
