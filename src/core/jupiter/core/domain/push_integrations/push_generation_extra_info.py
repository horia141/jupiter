"""Extra information for how to generate an inbox task."""
import argparse
import shlex
from typing import Optional

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.timezone import UTC, Timezone
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.framework.realm import (
    PROVIDE_VIA_REGISTRY,
    DatabaseRealm,
    RealmCodecRegistry,
    RealmDecoder,
    RealmDecodingError,
    RealmEncoder,
    RealmThing,
)
from jupiter.core.framework.value import CompositeValue, value


@value
class PushGenerationExtraInfo(CompositeValue):
    """Extra information for how to generate an inbox task."""

    timezone: Timezone
    name: Optional[InboxTaskName] = None
    status: Optional[InboxTaskStatus] = None
    eisen: Optional[Eisen] = None
    difficulty: Optional[Difficulty] = None
    actionable_date: Optional[ADate] = None
    due_date: Optional[ADate] = None


class PushGenerationExtraInfoDatabaseEncoder(
    RealmEncoder[PushGenerationExtraInfo, DatabaseRealm]
):
    """A database encoder for the extra info."""

    def encode(self, value: PushGenerationExtraInfo) -> RealmThing:
        """Encode a value."""
        string_pieces = []
        if value.name:
            string_pieces.append(f'--name="{value.name}"')
        if value.status:
            string_pieces.append(f"--status={value.status}")
        if value.eisen:
            string_pieces.append(f"--eisen={value.eisen}")
        if value.difficulty:
            string_pieces.append(f"--difficulty={value.difficulty}")
        if value.actionable_date:
            string_pieces.append(
                f"--actionable-date={value.actionable_date}",
            )
        if value.due_date:
            string_pieces.append(
                f"--due-date={value.due_date}",
            )
        return " ".join(string_pieces)


class PushGenerationExtraInfoDatabaseDecoder(
    RealmDecoder[PushGenerationExtraInfo, DatabaseRealm]
):
    """A database decoder for the extra info."""

    _realm_codec_registry: RealmCodecRegistry = PROVIDE_VIA_REGISTRY

    def decode(self, value: RealmThing) -> PushGenerationExtraInfo:
        """Decode a raw value."""
        if not (value is None or isinstance(value, str)):
            raise RealmDecodingError(
                f"Expected extra info to be a string or null, not {value.__class__.__name__}",
            )

        if value is None or not value.strip():
            return PushGenerationExtraInfo(
                timezone=UTC,
                name=None,
                status=None,
                eisen=None,
                difficulty=None,
                actionable_date=None,
                due_date=None,
            )

        parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
        parser.add_argument("--name", dest="name", help="The name of the inbox task")
        parser.add_argument(
            "--status",
            dest="status",
            choices=InboxTaskStatus.get_all_values(),
            help="The initial status of the inbox task",
        )
        parser.add_argument(
            "--eisen",
            dest="eisen",
            choices=Eisen.get_all_values(),
            help="The Eisenhower matrix values to use for task",
        )
        parser.add_argument(
            "--difficulty",
            dest="difficulty",
            choices=Difficulty.get_all_values(),
            help="The difficulty to use for tasks",
        )
        parser.add_argument(
            "--actionable-date",
            dest="actionable_date",
            help="The active date of the inbox task",
        )
        parser.add_argument(
            "--due-date",
            dest="due_date",
            help="The due date of the big plan",
        )

        try:
            # Browsers are sometimes happy to replace a "--" with a "—" (unicode "long-dash"
            # like https://www.compart.com/en/unicode/U+2015) or others which we must undo.
            rare_message_data = value.replace("—", "--").replace(
                "’", "'"  # noqa: RUF001
            )
            message_as_options = shlex.split(rare_message_data)

            args = parser.parse_args(args=message_as_options)

            return PushGenerationExtraInfo(
                timezone=UTC,
                name=self._realm_codec_registry.get_decoder(
                    InboxTaskName, DatabaseRealm
                ).decode(args.name)
                if args.name
                else None,
                status=self._realm_codec_registry.get_decoder(
                    InboxTaskStatus, DatabaseRealm
                ).decode(args.status)
                if args.status
                else None,
                eisen=self._realm_codec_registry.get_decoder(
                    Eisen, DatabaseRealm
                ).decode(args.eisen)
                if args.eisen
                else None,
                difficulty=self._realm_codec_registry.get_decoder(
                    Difficulty, DatabaseRealm
                ).decode(args.difficulty)
                if args.difficulty
                else None,
                actionable_date=self._realm_codec_registry.get_decoder(
                    ADate, DatabaseRealm
                ).decode(args.actionable_date)
                if args.actionable_date
                else None,
                due_date=self._realm_codec_registry.get_decoder(
                    ADate, DatabaseRealm
                ).decode(args.due_date)
                if args.due_date
                else None,
            )
        except ValueError as err:
            raise RealmDecodingError(
                f"Contents of extra info message `{value}` is invalid",
            ) from err
        except SystemExit as err:
            raise RealmDecodingError(
                f"Contents of extra info message `{value}`is invalid",
            ) from err
