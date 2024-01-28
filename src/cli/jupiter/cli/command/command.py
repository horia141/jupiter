"""Module for command base class."""

import abc
import argparse
import dataclasses
import types
import typing
from argparse import ArgumentParser, Namespace
from datetime import date, datetime
from typing import Any, Callable, Final, Generic, TypeVar, Union, cast, get_args, get_origin

import inflection
from jupiter.cli.command.rendering import RichConsoleProgressReporterFactory
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import LoggedInTopLevelContext, TopLevelContext
from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.user.user import User
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.realm import CliRealm, RealmCodecRegistry
from jupiter.core.framework.thing import Thing
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    UseCase,
    UseCaseContextBase,
    UseCaseSessionBase,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseResultBase
from jupiter.core.framework.value import (
    AtomicValue,
    CompositeValue,
    EnumValue,
    SecretValue,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppGuestMutationUseCase,
    AppGuestReadonlyUseCase,
    AppGuestUseCaseSession,
    AppLoggedInMutationUseCase,
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseSession,
)
from jupiter.core.utils.global_properties import GlobalProperties
from pendulum.date import Date
from pendulum.datetime import DateTime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class Command(abc.ABC):
    """The base class for command."""

    _postscript: Text | None = None

    @abc.abstractmethod
    def name(self) -> str:
        """The name of the command."""

    @abc.abstractmethod
    def description(self) -> str:
        """The description of the command."""

    @abc.abstractmethod
    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""

    @abc.abstractmethod
    async def run(
        self,
        console: Console,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""

    @property
    def should_appear_in_global_help(self) -> bool:
        """Should the command appear in the global help info or not."""
        return True

    def is_allowed_for_user(self, workspace: User) -> bool:
        """Is this command allowed for a particular user."""
        return True

    def is_allowed_for_workspace(self, workspace: Workspace) -> bool:
        """Is this command allowed for a particular workspace."""
        return True

    @property
    def should_have_streaming_progress_report(self) -> bool:
        """Whether the main script should have a streaming progress reporter."""
        return True

    def mark_postscript(self, postscript: Text) -> None:
        """Mark some postscript for the command."""
        self._postscript = postscript

    def get_postscript(self) -> Text | None:
        """Get some postscript for the command."""
        return self._postscript


UseCaseT = TypeVar("UseCaseT", bound=UseCase[Any, Any, Any, Any])
UseCaseSessionT = TypeVar("UseCaseSessionT", bound=UseCaseSessionBase)
UseCaseContextT = TypeVar("UseCaseContextT", bound=UseCaseContextBase)
UseCaseArgsT = TypeVar("UseCaseArgsT", bound=UseCaseArgsBase)
UseCaseResultT = TypeVar("UseCaseResultT", bound=UseCaseResultBase | None)

class UseCaseCommand(Generic[UseCaseT], Command, abc.ABC):
    """Base class for commands based on use cases."""

    _use_case: UseCaseT
    _args_type: type[UseCaseArgsBase]

    def __init__(self, use_case: UseCaseT) -> None:
        """Constructor."""
        self._use_case = use_case
        self._args_type = self._infer_args_class(use_case)

    def name(self) -> str:
        """The name of the command."""
        return inflection.dasherize(
            inflection.underscore(self._use_case.__class__.__name__)
        ).replace("-use-case", "")

    def description(self) -> str:
        """The description of the command."""
        return self._use_case.__doc__ or ""

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        self._build_parser_for_use_case_args(self._args_type, parser)

    @staticmethod
    def _infer_args_class(use_case: UseCaseT) -> type[UseCaseArgsBase]:
        use_case_type = use_case.__class__
        if not hasattr(use_case_type, "__orig_bases__"):
            raise Exception("No args class found")
        for base in use_case_type.__orig_bases__:  # type: ignore
            args = get_args(base)
            if len(args) > 0:
                return cast(type[UseCaseArgsBase], args[0])
        raise Exception("No args class found")

    @staticmethod
    def _build_parser_for_use_case_args(
        args_type: type[UseCaseArgsBase], parser: ArgumentParser
    ) -> None:
        def field_name_to_arg_name(field_name: str) -> str:
            return inflection.dasherize(field_name)

        def extract_field_type(
            field_type: type[Primitive | object],
        ) -> tuple[type[object], bool]:
            field_type_origin = get_origin(field_type)
            if field_type_origin is None:
                return field_type, False

            if field_type_origin is typing.Union or (
                isinstance(field_type_origin, type)
                and issubclass(field_type_origin, types.UnionType)
            ):
                field_args = get_args(field_type)
                if len(field_args) == 2 and (
                    field_args[0] is type(None) and field_args[1] is not type(None)
                ):
                    return field_args[1], True
                elif len(field_args) == 2 and (
                    field_args[1] is type(None) and field_args[0] is not type(None)
                ):
                    return field_args[0], True
                else:
                    raise Exception("Not implemented - union")
            else:
                return field_type, False

        def add_bool_field(
            field: dataclasses.Field[Thing],
        ) -> None:
            bool_field = parser.add_mutually_exclusive_group()
            bool_field.add_argument(
                f"--{field_name_to_arg_name(field.name)}",
                dest=field.name,
                default=field.default
                if field.default is not dataclasses.MISSING
                else False,
                action="store_true",
                help=field.metadata.get("help", ""),
            )
            bool_field.add_argument(
                f"--no-{field_name_to_arg_name(field.name)}",
                dest=field.name,
                default=field.default
                if field.default is not dataclasses.MISSING
                else False,
                action="store_false",
                help=field.metadata.get("help", ""),
            )

        def add_update_bool_field(
            field: dataclasses.Field[Thing],
        ) -> None:
            bool_field = parser.add_mutually_exclusive_group()
            bool_field.add_argument(
                f"--{field_name_to_arg_name(field.name)}",
                dest=field.name,
                default=None,
                action="store_true",
                help=field.metadata.get("help", ""),
            )
            bool_field.add_argument(
                f"--no-{field_name_to_arg_name(field.name)}",
                dest=field.name,
                default=None,
                action="store_false",
                help=field.metadata.get("help", ""),
            )

        def add_field(
            field: dataclasses.Field[Thing],
            field_type: type[int | float | str | date | datetime | Date | DateTime],
            field_optional: bool,
        ) -> None:
            if not field_optional:
                parser.add_argument(
                    f"--{field_name_to_arg_name(field.name)}",
                    dest=field.name,
                    required=True,
                    type=field_type if field_type in (int, float) else str,
                    help=field.metadata.get("help", ""),
                )
            else:
                a_field = parser.add_mutually_exclusive_group()
                a_field.add_argument(
                    f"--{field_name_to_arg_name(field.name)}",
                    dest=field.name,
                    required=False,
                    type=field_type if field_type in (int, float) else str,
                    default=field.default
                    if field.default is not dataclasses.MISSING
                    else None,
                    help=field.metadata.get("help", ""),
                )
                a_field.add_argument(
                    f"--no-{field_name_to_arg_name(field.name)}",
                    dest=field.name,
                    required=False,
                    action="store_const",
                    const=None,
                    help=field.metadata.get("help", ""),
                )

        def add_update_field(
            field: dataclasses.Field[Thing],
            field_type: type[int | float | str | date | datetime | Date | DateTime],
            field_optional: bool,
        ) -> None:
            if not field_optional:
                parser.add_argument(
                    f"--{field_name_to_arg_name(field.name)}",
                    dest=field.name,
                    required=False,
                    default=None,
                    type=field_type if field_type in (int, float) else str,
                    help=field.metadata.get("help", ""),
                )
            else:
                a_field = parser.add_mutually_exclusive_group()
                a_field.add_argument(
                    f"--{field_name_to_arg_name(field.name)}",
                    dest=field.name,
                    required=False,
                    type=field_type if field_type in (int, float) else str,
                    default=None,
                    help=field.metadata.get("help", ""),
                )
                a_field.add_argument(
                    f"--clear-{field_name_to_arg_name(field.name)}",
                    dest=f"clear_{field.name}",
                    required=False,
                    action="store_const",
                    const=True,
                    help=field.metadata.get("help", ""),
                )

        def add_field_list(
            field: dataclasses.Field[Thing],
            field_type: type[int | float | str | date | datetime | Date | DateTime],
            field_optional: bool,
        ) -> None:
            parser.add_argument(
                f"--{field_name_to_arg_name(field.name)}",
                dest=field.name,
                action="append",
                required=not field_optional,
                type=field_type if field_type in (int, float) else str,
                default=None,
                help=field.metadata.get("help", ""),
            )

        def add_enum_field(
            field: dataclasses.Field[Thing],
            field_type: type[EnumValue],
            field_optional: bool,
        ) -> None:
            parser.add_argument(
                f"--{field_name_to_arg_name(field.name)}",
                dest=field.name,
                required=not field_optional,
                choices=field_type.get_all_values(),
                help=field.metadata.get("help", ""),
            )

        def add_update_enum_field(
            field: dataclasses.Field[Thing],
            field_type: type[EnumValue],
            field_optional: bool,
        ) -> None:
            if not field_optional:
                parser.add_argument(
                    f"--{field_name_to_arg_name(field.name)}",
                    dest=field.name,
                    required=False,
                    default=None,
                    choices=field_type.get_all_values(),
                    help=field.metadata.get("help", ""),
                )
            else:
                a_field = parser.add_mutually_exclusive_group()
                a_field.add_argument(
                    f"--{field_name_to_arg_name(field.name)}",
                    dest=field.name,
                    required=False,
                    choices=field_type.get_all_values(),
                    default=None,
                    help=field.metadata.get("help", ""),
                )
                a_field.add_argument(
                    f"--clear-{field_name_to_arg_name(field.name)}",
                    dest=f"clear_{field.name}",
                    required=False,
                    action="store_const",
                    const=True,
                    help=field.metadata.get("help", ""),
                )

        def add_enum_field_list(
            field: dataclasses.Field[Thing],
            field_type: type[EnumValue],
            field_optional: bool,
        ) -> None:
            parser.add_argument(
                f"--{field_name_to_arg_name(field.name)}",
                dest=field.name,
                action="append",
                required=not field_optional,
                default=None,
                choices=field_type.get_all_values(),
                help=field.metadata.get("help", ""),
            )

        def add_update_field_list(
            field: dataclasses.Field[Thing],
            field_type: type[int | float | str | date | datetime | Date | DateTime],
            field_optional: bool,
        ) -> None:
            if not field_optional:
                parser.add_argument(
                    f"--{field_name_to_arg_name(field.name)}",
                    dest=field.name,
                    action="append",
                    required=False,
                    default=None,
                    type=field_type if field_type in (int, float) else str,
                    help=field.metadata.get("help", ""),
                )
            else:
                a_field = parser.add_mutually_exclusive_group()
                a_field.add_argument(
                    f"--{field_name_to_arg_name(field.name)}",
                    dest=field.name,
                    action="append",
                    required=False,
                    type=field_type if field_type in (int, float) else str,
                    default=None,
                    help=field.metadata.get("help", ""),
                )
                a_field.add_argument(
                    f"--clear-{field_name_to_arg_name(field.name)}",
                    dest=f"clear_{field.name}",
                    required=False,
                    action="store_const",
                    const=True,
                    help=field.metadata.get("help", ""),
                )

        def process_one_concept(a_thing: type[UseCaseArgsBase]) -> None:
            all_fields = dataclasses.fields(a_thing)

            for field in all_fields:
                field_type, field_optional = extract_field_type(field.type)

                if field_type is bool:
                    add_bool_field(field)
                elif isinstance(field_type, type) and issubclass(
                    field_type, (int, float, str, date, datetime, Date, DateTime)
                ):
                    add_field(field, field_type, field_optional)
                elif (
                    isinstance(field_type, type)
                    and get_origin(field_type) is None
                    and issubclass(field_type, AtomicValue)
                ):
                    basic_field_type = field_type.base_type_hack()
                    if basic_field_type is bool:
                        add_bool_field(field)
                    elif issubclass(
                        basic_field_type,
                        (int, float, str, date, datetime, Date, DateTime),
                    ):
                        add_field(field, basic_field_type, field_optional)
                    else:
                        raise Exception(
                            f"Unsupported field type {field_type}+{basic_field_type} for {args_type.__name__}:{field.name}"
                        )
                elif (
                    isinstance(field_type, type)
                    and get_origin(field_type) is None
                    and issubclass(field_type, CompositeValue)
                ):
                    raise Exception(
                        f"Unsupported fiedl type {field_type}+{basic_field_type} for {args_type.__name__}:{field.name}"
                    )
                elif (
                    isinstance(field_type, type)
                    and get_origin(field_type) is None
                    and issubclass(field_type, EnumValue)
                ):
                    add_enum_field(field, field_type, field_optional)
                elif (
                    isinstance(field_type, type)
                    and get_origin(field_type) is None
                    and issubclass(field_type, SecretValue)
                ):
                    add_field(field, str, field_optional)
                elif get_origin(field_type) is not None:
                    origin_field_type = get_origin(field_type)
                    if origin_field_type is UpdateAction:
                        update_field = get_args(field_type)[0]
                        update_field_type, update_field_optional = extract_field_type(
                            update_field
                        )

                        if update_field_type is bool:
                            add_update_bool_field(field)
                        elif (
                            isinstance(update_field_type, type)
                            and get_origin(update_field_type) is None
                            and issubclass(
                                update_field_type,
                                (int, float, str, date, datetime, Date, DateTime),
                            )
                        ):
                            add_update_field(
                                field, update_field_type, update_field_optional
                            )
                        elif (
                            isinstance(update_field_type, type)
                            and get_origin(update_field_type) is None
                            and issubclass(update_field_type, AtomicValue)
                        ):
                            basic_update_field_type = update_field_type.base_type_hack()
                            if basic_update_field_type is bool:
                                add_bool_field(field)
                            elif issubclass(
                                basic_update_field_type,
                                (int, float, str, date, datetime, Date, DateTime),
                            ):
                                add_update_field(
                                    field,
                                    basic_update_field_type,
                                    update_field_optional,
                                )
                            else:
                                raise Exception(
                                    f"Unsupported field type {field_type}+{basic_field_type} for {args_type.__name__}:{field.name}"
                                )
                        elif (
                            isinstance(update_field_type, type)
                            and get_origin(update_field_type) is None
                            and issubclass(update_field_type, EnumValue)
                        ):
                            add_update_enum_field(
                                field, update_field_type, update_field_optional
                            )
                        elif get_origin(update_field_type) is not None:
                            origin_update_field_type = get_origin(update_field_type)
                            if origin_update_field_type in (list, set):
                                update_field_list_item = get_args(update_field_type)[0]
                                (
                                    update_field_list_item_type,
                                    update_field_list_item_optional,
                                ) = extract_field_type(update_field_list_item)
                                if (
                                    isinstance(update_field_list_item_type, type)
                                    and get_origin(update_field_list_item_type) is None
                                    and issubclass(
                                        update_field_list_item_type,
                                        (
                                            int,
                                            float,
                                            str,
                                            date,
                                            datetime,
                                            Date,
                                            DateTime,
                                        ),
                                    )
                                ):
                                    add_update_field_list(
                                        field,
                                        update_field_list_item_type,
                                        update_field_list_item_optional,
                                    )
                                elif (
                                    isinstance(update_field_list_item_type, type)
                                    and get_origin(update_field_list_item_type) is None
                                    and issubclass(
                                        update_field_list_item_type, AtomicValue
                                    )
                                ):
                                    basic_field_item_type_type = (
                                        update_field_list_item_type.base_type_hack()
                                    )
                                    if issubclass(
                                        basic_field_item_type_type,
                                        (
                                            int,
                                            float,
                                            str,
                                            date,
                                            datetime,
                                            Date,
                                            DateTime,
                                        ),
                                    ):
                                        add_update_field_list(
                                            field,
                                            basic_field_item_type_type,
                                            update_field_list_item_optional,
                                        )
                                    else:
                                        raise Exception(
                                            f"Unsupported field type {field_type}+{basic_field_type} for {args_type.__name__}:{field.name}"
                                        )
                                else:
                                    raise Exception(
                                        f"Unsupported field type {field_type} for {args_type.__name__}:{field.name}"
                                    )
                            else:
                                raise Exception(
                                    f"Unsupported field type {field_type} for {args_type.__name__}:{field.name}"
                                )
                        else:
                            raise Exception(
                                f"Unsupported field type {field_type} for {args_type.__name__}:{field.name}"
                            )
                    elif origin_field_type in (list, set):
                        list_item_type = get_args(field_type)[0]
                        if list_item_type in (
                            int,
                            float,
                            str,
                            date,
                            datetime,
                            Date,
                            DateTime,
                        ):
                            add_field_list(field, list_item_type, field_optional)
                        elif (
                            isinstance(list_item_type, type)
                            and get_origin(list_item_type) is None
                            and issubclass(list_item_type, AtomicValue)
                        ):
                            basic_field_type = list_item_type.base_type_hack()
                            if issubclass(
                                basic_field_type,
                                (int, float, str, date, datetime, Date, DateTime),
                            ):
                                add_field_list(field, basic_field_type, field_optional)
                            else:
                                raise Exception(
                                    f"Unsupported field type {field_type}+{basic_field_type} for {args_type.__name__}:{field.name}"
                                )
                        elif (
                            isinstance(list_item_type, type)
                            and get_origin(list_item_type) is None
                            and issubclass(list_item_type, EnumValue)
                        ):
                            add_enum_field_list(field, list_item_type, field_optional)
                        else:
                            raise Exception(
                                f"Unsupported field type {field_type} for {args_type.__name__}:{field.name}"
                            )
                    elif origin_field_type == dict:
                        raise Exception(
                            f"Unsupported field type {field_type} for {args_type.__name__}:{field.name}"
                        )
                    else:
                        raise Exception(
                            f"Unsupported field type {field_type} for {args_type.__name__}:{field.name}"
                        )
                else:
                    raise Exception(
                        f"Unsupported field type {field_type} for {args_type.__name__}:{field.name}"
                    )

        process_one_concept(args_type)


GuestMutationCommandUseCase = TypeVar(
    "GuestMutationCommandUseCase", bound=AppGuestMutationUseCase[Any, Any]
)


class GuestMutationCommand(
    Generic[GuestMutationCommandUseCase],
    UseCaseCommand[GuestMutationCommandUseCase],
    abc.ABC,
):
    """Base class for commands which do not require authentication."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _session_storage: Final[SessionStorage]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        session_storage: SessionStorage,
        use_case: GuestMutationCommandUseCase) -> None:
        """Constructor."""
        super().__init__(use_case)
        self._realm_codec_registry = realm_codec_registry
        self._session_storage = session_storage

    async def run(
        self,
        console: Console,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        session_info = self._session_storage.load_optional()
        await self._run(console, session_info, args)

    async def _run(
        self,
        console: Console,
        session_info: SessionInfo | None,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        parsed_args = self._realm_codec_registry.get_decoder(
            self._args_type, CliRealm
        ).decode(vars(args))
        result = await self._use_case.execute(
            AppGuestUseCaseSession(
                session_info.auth_token_ext if session_info else None
            ),
            parsed_args,
        )
        self._render_result(console, result)

    def _render_result(self, console: Console, result: UseCaseResultT) -> None:
        """Render the result."""


GuestReadonlyCommandUseCase = TypeVar(
    "GuestReadonlyCommandUseCase", bound=AppGuestReadonlyUseCase[Any, Any]
)


class GuestReadonlyCommand(
    Generic[GuestReadonlyCommandUseCase],
    UseCaseCommand[GuestReadonlyCommandUseCase],
    abc.ABC,
):
    """Base class for commands which just read and present data."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _session_storage: Final[SessionStorage]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        session_storage: SessionStorage,
        use_case: GuestReadonlyCommandUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(use_case)
        self._realm_codec_registry = realm_codec_registry
        self._session_storage = session_storage

    async def run(
        self,
        console: Console,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        session_info = self._session_storage.load_optional()
        await self._run(console, session_info, args)

    async def _run(
        self,
        console: Console,
        session_info: SessionInfo | None,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        parsed_args = self._realm_codec_registry.get_decoder(
            self._args_type, CliRealm
        ).decode(vars(args))
        result = await self._use_case.execute(
            AppGuestUseCaseSession(
                session_info.auth_token_ext if session_info else None
            ),
            parsed_args,
        )
        self._render_result(console, result)

    def _render_result(self, console: Console, result: UseCaseResultT) -> None:
        """Render the result."""

    @property
    def should_have_streaming_progress_report(self) -> bool:
        """Whether the main script should have a streaming progress reporter."""
        return False


LoggedInMutationCommandUseCase = TypeVar(
    "LoggedInMutationCommandUseCase", bound=AppLoggedInMutationUseCase[Any, Any]
)


class LoggedInMutationCommand(
    Generic[LoggedInMutationCommandUseCase],
    UseCaseCommand[LoggedInMutationCommandUseCase],
    abc.ABC,
):
    """Base class for commands which require authentication."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _session_storage: Final[SessionStorage]
    _top_level_context: Final[LoggedInTopLevelContext]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        use_case: LoggedInMutationCommandUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(use_case)
        self._realm_codec_registry = realm_codec_registry
        self._session_storage = session_storage
        self._top_level_context = top_level_context

    async def run(
        self,
        console: Console,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        session_info = self._session_storage.load()
        await self._run(console, session_info, args)

    async def _run(
        self,
        console: Console,
        session: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        parsed_args = self._realm_codec_registry.get_decoder(
            self._args_type, CliRealm
        ).decode(vars(args))
        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session.auth_token_ext),
            parsed_args,
        )
        self._render_result(console, result)

    def _render_result(self, console: Console, result: UseCaseResultT) -> None:
        """Render the result."""

    def is_allowed_for_user(self, user: User) -> bool:
        """Is this command allowed for a particular user."""
        scoped_feature = self._use_case.get_scoped_to_feature()
        if scoped_feature is None:
            return True
        if isinstance(scoped_feature, UserFeature):
            return user.is_feature_available(scoped_feature)
        elif isinstance(scoped_feature, WorkspaceFeature):
            return True
        for feature in scoped_feature:
            if isinstance(feature, UserFeature):
                if not user.is_feature_available(feature):
                    return False
        return True

    def is_allowed_for_workspace(self, workspace: Workspace) -> bool:
        """Is this command allowed for a particular workspace."""
        scoped_feature = self._use_case.get_scoped_to_feature()
        if scoped_feature is None:
            return True
        if isinstance(scoped_feature, UserFeature):
            return True
        elif isinstance(scoped_feature, WorkspaceFeature):
            return workspace.is_feature_available(scoped_feature)
        for feature in scoped_feature:
            if isinstance(feature, WorkspaceFeature):
                if not workspace.is_feature_available(feature):
                    return False
        return True


LoggedInReadonlyCommandUseCase = TypeVar(
    "LoggedInReadonlyCommandUseCase", bound=AppLoggedInReadonlyUseCase[Any, Any]
)


class LoggedInReadonlyCommand(
    Generic[LoggedInReadonlyCommandUseCase],
    UseCaseCommand[LoggedInReadonlyCommandUseCase],
    abc.ABC,
):
    """Base class for commands which just read and present data."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _session_storage: Final[SessionStorage]
    _top_level_context: Final[LoggedInTopLevelContext]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        session_storage: SessionStorage,
        top_level_context: LoggedInTopLevelContext,
        use_case: LoggedInReadonlyCommandUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(use_case)
        self._realm_codec_registry = realm_codec_registry
        self._session_storage = session_storage
        self._top_level_context = top_level_context

    async def run(
        self,
        console: Console,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        session_info = self._session_storage.load()
        await self._run(console, session_info, args)

    async def _run(
        self,
        console: Console,
        session: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        parsed_args = self._realm_codec_registry.get_decoder(
            self._args_type, CliRealm
        ).decode(vars(args))
        result = await self._use_case.execute(
            AppLoggedInUseCaseSession(session.auth_token_ext),
            parsed_args,
        )
        self._render_result(console, result)

    def _render_result(self, console: Console, result: UseCaseResultT) -> None:
        """Render the result."""

    def is_allowed_for_user(self, user: User) -> bool:
        """Is this command allowed for a particular user."""
        scoped_feature = self._use_case.get_scoped_to_feature()
        if scoped_feature is None:
            return True
        if isinstance(scoped_feature, UserFeature):
            return user.is_feature_available(scoped_feature)
        elif isinstance(scoped_feature, WorkspaceFeature):
            return True
        for feature in scoped_feature:
            if isinstance(feature, UserFeature):
                if not user.is_feature_available(feature):
                    return False
        return True

    def is_allowed_for_workspace(self, workspace: Workspace) -> bool:
        """Is this command allowed for a particular workspace."""
        scoped_feature = self._use_case.get_scoped_to_feature()
        if scoped_feature is None:
            return True
        if isinstance(scoped_feature, UserFeature):
            return True
        elif isinstance(scoped_feature, WorkspaceFeature):
            return workspace.is_feature_available(scoped_feature)
        for feature in scoped_feature:
            if isinstance(feature, WorkspaceFeature):
                if not workspace.is_feature_available(feature):
                    return False
        return True

    @property
    def should_have_streaming_progress_report(self) -> bool:
        """Whether the main script should have a streaming progress reporter."""
        return False


class TestHelperCommand(Command, abc.ABC):
    """Base class for commands used in tests."""

    @property
    def should_appear_in_global_help(self) -> bool:
        """Should the command appear in the global help info or not."""
        return False

    @property
    def should_have_streaming_progress_report(self) -> bool:
        """Whether the main script should have a streaming progress reporter."""
        return False
    

class CliApp:
    """A CLI application."""

    @dataclasses.dataclass
    class GuestMutationEntry:
        """A guest mutation use case entry."""

        use_case: AppGuestMutationUseCase[UseCaseArgsBase, UseCaseResultBase]

    @dataclasses.dataclass
    class GuestReadonlyEntry:
        """A guest readonly use case entry."""

        use_case: AppGuestReadonlyUseCase[UseCaseArgsBase, UseCaseResultBase]

    @dataclasses.dataclass
    class LoggedInMutationEntry:
        """A logged in mutation use case entry."""

        use_case: AppLoggedInMutationUseCase[UseCaseArgsBase, UseCaseResultBase]

    @dataclasses.dataclass
    class LoggedInReadonlyEntry:
        """A logged in readonly use case entry."""

        use_case: AppLoggedInReadonlyUseCase[UseCaseArgsBase, UseCaseResultBase]

    _global_properties: Final[GlobalProperties]
    _top_level_context: Final[TopLevelContext]
    _console: Final[Console]
    _progress_reporter_factory: Final[RichConsoleProgressReporterFactory]
    _realm_codec_registry: Final[RealmCodecRegistry]
    _session_storage: Final[SessionStorage]
    _commands: Final[list[Command]]
    _guest_mutation_use_cases: Final[list[GuestMutationEntry]]
    _guest_readonly_use_cases: Final[list[GuestReadonlyEntry]]
    _loggedin_mutation_use_cases: Final[list[LoggedInMutationEntry]]
    _loggedin_readonly_use_cases: Final[list[LoggedInReadonlyEntry]]

    def __init__(
        self,
        global_properties: GlobalProperties,
        top_level_context: TopLevelContext,
        console: Console,
        progress_reporter_factory: RichConsoleProgressReporterFactory,
        realm_codec_registry: RealmCodecRegistry,
        session_storage: SessionStorage,
    ) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._top_level_context = top_level_context
        self._console = console
        self._progress_reporter_factory = progress_reporter_factory
        self._realm_codec_registry = realm_codec_registry
        self._session_storage = session_storage
        self._commands = []
        self._guest_readonly_use_cases = []
        self._guest_mutation_use_cases = []
        self._loggedin_readonly_use_cases = []
        self._loggedin_mutation_use_cases = []

    def add_command(
        self,
        command: Command,
    ) -> "CliApp":
        """Add a command to the app."""
        self._commands.append(command)
        return self

    def add_use_case(
        self,
        use_case: UseCase[
            UseCaseSessionT, UseCaseContextT, UseCaseArgsT, UseCaseResultT
        ],
    ) -> "CliApp":
        """Add a use case to the app."""
        if isinstance(use_case, AppGuestMutationUseCase):
            self._guest_mutation_use_cases.append(
                CliApp.GuestMutationEntry(use_case=use_case)
            )
        elif isinstance(use_case, AppGuestReadonlyUseCase):
            self._guest_readonly_use_cases.append(
                CliApp.GuestReadonlyEntry(use_case=use_case)
            )
        elif isinstance(use_case, AppLoggedInMutationUseCase):
            self._loggedin_mutation_use_cases.append(
                CliApp.LoggedInMutationEntry(use_case=use_case)
            )
        elif isinstance(use_case, AppLoggedInReadonlyUseCase):
            self._loggedin_readonly_use_cases.append(
                CliApp.LoggedInReadonlyEntry(use_case=use_case)
            )
        else:
            raise Exception(f"Unsupported use case type {use_case}")

        return self

    async def run(self, argv: list[str]) -> None:
        """Run the app."""
        commands: list[Command] = list(self._commands)

        for use_case_gm in self._guest_mutation_use_cases:
            commands.append(
                GuestMutationCommand(
                    realm_codec_registry=self._realm_codec_registry,
                    session_storage=self._session_storage,
                    use_case=use_case_gm.use_case,
                )
            )

        for use_case_gr in self._guest_readonly_use_cases:
            commands.append(
                GuestReadonlyCommand(
                    realm_codec_registry=self._realm_codec_registry,
                    session_storage=self._session_storage,
                    use_case=use_case_gr.use_case,
                )
            )

        for use_case_lm in self._loggedin_mutation_use_cases:
            commands.append(
                LoggedInMutationCommand(
                    realm_codec_registry=self._realm_codec_registry,
                    session_storage=self._session_storage,
                    top_level_context=self._top_level_context.to_logged_in(),
                    use_case=use_case_lm.use_case,
                )
            )

        for use_case_lr in self._loggedin_readonly_use_cases:
            commands.append(
                LoggedInReadonlyCommand(
                    realm_codec_registry=self._realm_codec_registry,
                    session_storage=self._session_storage,
                    top_level_context=self._top_level_context.to_logged_in(),
                    use_case=use_case_lr.use_case,
                )
            )

        parser = argparse.ArgumentParser(
            description=self._global_properties.description
        )
        parser.add_argument(
            "--version",
            dest="just_show_version",
            action="store_const",
            default=False,
            const=True,
            help="Show the version of the application",
        )

        subparsers = parser.add_subparsers(
            dest="subparser_name",
            help="Sub-command help",
            metavar="{command}",
        )

        for command in commands:
            if (
                command.should_appear_in_global_help
                and (
                    self._top_level_context.user is None
                    or command.is_allowed_for_user(self._top_level_context.user)
                )
                and (
                    self._top_level_context.workspace is None
                    or command.is_allowed_for_workspace(
                        self._top_level_context.workspace
                    )
                )
            ):
                command_parser = subparsers.add_parser(
                    command.name(),
                    help=command.description(),
                    description=command.description(),
                )
            else:
                command_parser = subparsers.add_parser(
                    command.name(),
                    description=command.description(),
                )
            command.build_parser(command_parser)

        args = parser.parse_args(argv[1:])

        if args.just_show_version:
            print(
                f"{self._global_properties.description} {self._global_properties.version}"
            )
            return

        for command in commands:
            if args.subparser_name != command.name():
                continue

            with self._progress_reporter_factory.envelope(
                command.should_have_streaming_progress_report, command.name(), args
            ):
                await command.run(self._console, args)

            command_postscript = command.get_postscript()
            if command_postscript is not None:
                postscript_panel = Panel(
                    command_postscript, title="PS.", title_align="left"
                )
                self._console.print(postscript_panel)

            break
