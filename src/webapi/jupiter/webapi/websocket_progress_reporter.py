"""Progress reporter that uses a websocket to push progress updates."""
import asyncio
import logging
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import (
    AsyncIterator,
    DefaultDict,
    Dict,
    Final,
    List,
    Optional,
    Set,
    Tuple,
)

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.json import JSONDictType
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    EntityProgressReporter,
    MarkProgressStatus,
    ProgressReporterFactory,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseContext
from starlette.websockets import WebSocket
from websockets.exceptions import ConnectionClosedError

LOGGER = logging.getLogger(__name__)


class _WebsocketHandle:
    """A temporary handle for a websocket."""

    _websocket: Optional[WebSocket]
    _send_tasks_ref: Final[Set[asyncio.Task[None]]]

    def __init__(self, websocket: Optional[WebSocket]) -> None:
        """Constructor."""
        self._websocket = websocket
        self._send_tasks_ref = set()

    @staticmethod
    def with_websocket(websocket: WebSocket) -> "_WebsocketHandle":
        """Construct a handle bound to a websocket."""
        return _WebsocketHandle(websocket)

    @staticmethod
    def with_no_websocket() -> "_WebsocketHandle":
        """Construct a handle that isn't bound to a websocket."""
        return _WebsocketHandle(None)

    async def replace_websocket(self, websocket: WebSocket) -> None:
        """Replace the websocket we have with a new one."""
        if self._websocket is not None:
            self._cancel_pending_sends()
            await self._websocket.close()
        self._websocket = websocket

    async def clear_websocket(self) -> None:
        """Clear the websocket."""
        if self._websocket is not None:
            self._cancel_pending_sends()
            await self._websocket.close()
        self._websocket = None

    async def send_json(self, data: JSONDictType) -> None:
        """Send some json down the websocket."""
        loop = asyncio.get_running_loop()
        task = loop.create_task(self._try_send_json(data))
        self._send_tasks_ref.add(task)
        task.add_done_callback(self._send_tasks_ref.discard)

    def _cancel_pending_sends(self) -> None:
        """Cancel any pending sends."""
        for task in self._send_tasks_ref:
            task.cancel()

    async def _try_send_json(self, data: JSONDictType) -> None:
        if self._websocket is None:
            return
        try:
            await self._websocket.send_json(data)
        except ConnectionClosedError:
            # Other side bailed on us.
            LOGGER.warning(
                "Progress reporter websocket connection got closed unexpectedly.",
            )
            self._websocket = None


class WebsocketEntityProgressReporter(EntityProgressReporter):
    """A progress reporter for a particular entity."""

    _websocket: Final[_WebsocketHandle]
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
        websocket: _WebsocketHandle,
        entity_type: str,
        action_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
        print_indent: int = 0,
    ) -> None:
        """Constructor."""
        self._websocket = websocket
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
        await self._send_status_update(self.to_str_form())
        return self

    async def mark_known_name(self, name: str) -> EntityProgressReporter:
        """Mark the fact that we now know the entity name for the entity being processed."""
        self._entity_name = name
        await self._send_status_update(self.to_str_form())
        return self

    async def mark_local_change(self) -> EntityProgressReporter:
        """Mark the fact that the local change has succeeded."""
        self._local_change_status = MarkProgressStatus.OK
        await self._send_status_update(self.to_str_form())
        return self

    async def mark_remote_change(
        self,
        success: MarkProgressStatus = MarkProgressStatus.OK,
    ) -> EntityProgressReporter:
        """Mark the fact that the remote change has completed."""
        self._remote_change_status = success
        await self._send_status_update(self.to_str_form())
        return self

    async def mark_other_progress(
        self,
        progress: str,
        success: MarkProgressStatus = MarkProgressStatus.OK,
    ) -> EntityProgressReporter:
        """Mark some other type of progress."""
        self._progresses.append((progress, success))
        await self._send_status_update(self.to_str_form())
        return self

    def to_str_form(self) -> str:
        """Prepare the intermediary string form for this one."""
        text = f"Working on {self._action_type} {self._entity_type}"
        if self._entity_id is not None:
            text += " "
            text += str(self._entity_id)
        if self._entity_name is not None:
            text += " "
            text += self._entity_name
        if self._local_change_status is not None:
            if self._local_change_status == MarkProgressStatus.PROGRESS:
                text += " 🧭 local"
            elif self._local_change_status == MarkProgressStatus.OK:
                text += " ✅ local"
            elif self._local_change_status == MarkProgressStatus.FAILED:
                text += " ⭕ local"
            else:
                text += " ☑️  local"
        if self._remote_change_status is not None:
            if self._remote_change_status == MarkProgressStatus.PROGRESS:
                text += " 🧭 remote"
            elif self._remote_change_status == MarkProgressStatus.OK:
                text += " ✅ remote"
            elif self._remote_change_status == MarkProgressStatus.FAILED:
                text += " ⭕ remote"
            else:
                text += " ☑️ local"
        for progress, progress_status in self._progresses:
            if progress_status == MarkProgressStatus.PROGRESS:
                text += f" 🧭 {progress}"
            elif progress_status == MarkProgressStatus.OK:
                text += f" ✅ {progress}"
            elif progress_status == MarkProgressStatus.FAILED:
                text += f" ⭕ {progress}"
            else:
                text += f" ☑️  {progress}"

        return text

    def to_final_str_form(self) -> str:
        """Prepare the final string form for this one."""
        text = (
            self._print_indent * ".."
            + f"Done with {self._action_type} {self._entity_type}"
        )
        if self._entity_id is not None:
            text += " "
            text += str(self._entity_id)
        if self._entity_name is not None:
            text += " "
            text += self._entity_name
        if self._local_change_status is not None:
            if self._local_change_status == MarkProgressStatus.PROGRESS:
                text += " 🧭 local"
            elif self._local_change_status == MarkProgressStatus.OK:
                text += " ✅ local"
            elif self._local_change_status == MarkProgressStatus.FAILED:
                text += " ⭕ local"
            else:
                text += " ☑️  local"
        if self._remote_change_status is not None:
            if self._remote_change_status == MarkProgressStatus.PROGRESS:
                text += " 🧭 remote"
            elif self._remote_change_status == MarkProgressStatus.OK:
                text += " ✅ remote"
            elif self._remote_change_status == MarkProgressStatus.FAILED:
                text += " ⭕ remote"
            else:
                text += " ☑️ remote"
        for progress, progress_status in self._progresses:
            if progress_status == MarkProgressStatus.PROGRESS:
                text += f" 🧭 {progress}"
            elif progress_status == MarkProgressStatus.OK:
                text += f" ✅ {progress}"
            elif progress_status == MarkProgressStatus.FAILED:
                text += f" ⭕ {progress}"
            else:
                text += f" ☑️  {progress}"
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

    async def _send_status_update(self, message: str) -> None:
        await self._websocket.send_json(
            {
                "type": "status-update",
                "message": message,
                "entity_type": self._entity_type,
                "entity_id": str(self._entity_id) if self._entity_id else None,
                "entity_name": self._entity_name,
            },
        )


class WebsocketContextProgressReporter(ContextProgressReporter):
    """A progress reporter based on a Rich console that outputs progress to the console."""

    _websocket: Final[_WebsocketHandle]
    _sections: Final[List[str]]
    _created_entities_stats: Final[DefaultDict[str, List[Tuple[str, EntityId]]]]
    _updated_entities_stats: Final[DefaultDict[str, int]]
    _archived_entities_stats: Final[DefaultDict[str, int]]
    _removed_entities_stats: Final[DefaultDict[str, int]]
    _print_indent: Final[int]
    _is_needed: bool

    def __init__(
        self,
        websocket: _WebsocketHandle,
        sections: List[str],
        created_entities_stats: DefaultDict[str, List[Tuple[str, EntityId]]],
        updated_entities_stats: DefaultDict[str, int],
        archived_entities_stats: DefaultDict[str, int],
        removed_entities_stats: DefaultDict[str, int],
        print_indent: int,
    ) -> None:
        """Constructor."""
        self._websocket = websocket
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
        section_text = self._sections[0]
        for section_title in self._sections[1:]:
            section_text += " // "
            section_text += section_title
        await self._send_section(section_text)
        yield None
        self._sections.pop()

    @asynccontextmanager
    async def start_creating_entity(
        self,
        entity_type: str,
        entity_name: str,
    ) -> AsyncIterator[WebsocketEntityProgressReporter]:
        """Report that a particular entity is being created."""
        entity_progress_reporter = WebsocketEntityProgressReporter(
            self._websocket,
            entity_type,
            "creating",
            entity_name=entity_name,
            print_indent=self._print_indent,
        )

        await self._send_status_create(
            entity_progress_reporter.to_str_form(),
            entity_type,
            None,
            entity_name,
        )

        yield entity_progress_reporter

        if entity_progress_reporter.is_needed:
            self._created_entities_stats[entity_type].append(
                (entity_name, entity_progress_reporter.entity_id),
            )
            await self._send_status_finish(
                entity_progress_reporter.to_final_str_form(),
                entity_type,
                None,
                entity_name,
            )
            self._is_needed = True
        else:
            await self._send_status_clear()

    @asynccontextmanager
    async def start_updating_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> AsyncIterator[WebsocketEntityProgressReporter]:
        """Report that a particular entity is being updated."""
        entity_progress_reporter = WebsocketEntityProgressReporter(
            self._websocket,
            entity_type,
            "updating",
            entity_id=entity_id,
            entity_name=entity_name,
            print_indent=self._print_indent,
        )

        await self._send_status_create(
            entity_progress_reporter.to_str_form(),
            entity_type,
            entity_id,
            entity_name,
        )

        yield entity_progress_reporter

        if entity_progress_reporter.is_needed:
            self._updated_entities_stats[entity_type] += 1
            await self._send_status_finish(
                entity_progress_reporter.to_final_str_form(),
                entity_type,
                entity_id,
                entity_name,
            )
            self._is_needed = True
        else:
            await self._send_status_clear()

    @asynccontextmanager
    async def start_archiving_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> AsyncIterator[WebsocketEntityProgressReporter]:
        """Report that a particular entity is being archived."""
        entity_progress_reporter = WebsocketEntityProgressReporter(
            self._websocket,
            entity_type,
            "archiving",
            entity_id=entity_id,
            entity_name=entity_name,
            print_indent=self._print_indent,
        )

        await self._send_status_create(
            entity_progress_reporter.to_str_form(),
            entity_type,
            entity_id,
            entity_name,
        )

        yield entity_progress_reporter

        if entity_progress_reporter.is_needed:
            self._archived_entities_stats[entity_type] += 1
            await self._send_status_finish(
                entity_progress_reporter.to_final_str_form(),
                entity_type,
                entity_id,
                entity_name,
            )
            self._is_needed = True
        else:
            await self._send_status_clear()

    @asynccontextmanager
    async def start_removing_entity(
        self,
        entity_type: str,
        entity_id: Optional[EntityId] = None,
        entity_name: Optional[str] = None,
    ) -> AsyncIterator[WebsocketEntityProgressReporter]:
        """Report that a particular entity is being removed."""
        entity_progress_reporter = WebsocketEntityProgressReporter(
            self._websocket,
            entity_type,
            "removing",
            entity_id=entity_id,
            entity_name=entity_name,
            print_indent=self._print_indent,
        )

        await self._send_status_create(
            entity_progress_reporter.to_str_form(),
            entity_type,
            entity_id,
            entity_name,
        )

        yield entity_progress_reporter

        if entity_progress_reporter.is_needed:
            self._removed_entities_stats[entity_type] += 1
            await self._send_status_finish(
                entity_progress_reporter.to_final_str_form(),
                entity_type,
                entity_id,
                entity_name,
            )
            self._is_needed = True
        else:
            await self._send_status_clear()

    @asynccontextmanager
    async def start_complex_entity_work(
        self,
        entity_type: str,
        entity_id: EntityId,
        entity_name: str,
    ) -> AsyncIterator[ContextProgressReporter]:
        """Create a progress reporter with some scoping to operate with subentities of a main entity."""
        subprogress_reporter = WebsocketContextProgressReporter(
            websocket=self._websocket,
            sections=[],
            created_entities_stats=self._created_entities_stats,
            updated_entities_stats=self._updated_entities_stats,
            archived_entities_stats=self._archived_entities_stats,
            removed_entities_stats=self._removed_entities_stats,
            print_indent=self._print_indent + 1,
        )

        # header_text = Text(f"Working on {entity_type} ")
        # header_text.append(entity_id_to_rich_text(entity_id))
        # header_text.append(" ")
        # header_text.append(entity_name)
        #
        # self._console.print(header_text)
        # time.sleep(0.01)  # Oh so ugly
        #
        yield subprogress_reporter
        #
        # if subprogress_reporter.is_needed:
        #     self._is_needed = True
        # else:
        #     self._status.stop()
        #     self._console.control(Control.move_to_column(0, -1))
        #     self._status.start()
        #
        # self._status.update("Working on it ...")

    def print_prologue(self, command_name: str, argv: List[str]) -> None:
        """Print a prologue section."""
        # command_text = Text(f"{command_name}")
        # if len(argv) > 1:
        #     command_text.append(f" {' '.join(argv[1:])}")
        # command_text.stylize("green on blue bold underline")
        #
        # prologue_text = Text("Running command ").append(command_text)
        # panel = Panel(prologue_text)
        # self._console.print(panel)

    def print_epilogue(self) -> None:
        """Print a prologue section."""
        # epilogue_tree = Tree("Results:", guide_style="bold bright_blue")
        # if len(self._created_entities_stats):
        #     created_tree = epilogue_tree.add("Created:")
        #     for (
        #         entity_type,
        #         created_entity_list,
        #     ) in self._created_entities_stats.items():
        #         entity_count = len(created_entity_list)
        #         entity_type_tree = created_tree.add(
        #             f"{entity_type} => {entity_count} in total", guide_style="blue"
        #         )
        #         for entity_name, entity_id in created_entity_list:
        #             created_entity_text = Text("")
        #             created_entity_text.append(entity_id_to_rich_text(entity_id))
        #             created_entity_text.append(" ")
        #             created_entity_text.append(
        #                 entity_name_to_rich_text(EntityName.from_raw(entity_name))
        #             )
        #             entity_type_tree.add(created_entity_text)
        # if len(self._updated_entities_stats):
        #     updated_tree = epilogue_tree.add("Updated:")
        #     for entity_type, entity_count in self._updated_entities_stats.items():
        #         updated_tree.add(
        #             f"{entity_type} => {entity_count} in total", guide_style="blue"
        #         )
        # if len(self._archived_entities_stats):
        #     archived_tree = epilogue_tree.add("Archived:")
        #     for entity_type, entity_count in self._archived_entities_stats.items():
        #         archived_tree.add(
        #             f"{entity_type} => {entity_count} in total", guide_style="blue"
        #         )
        # if len(self._removed_entities_stats):
        #     removed_tree = epilogue_tree.add("Removed:")
        #     for entity_type, entity_count in self._removed_entities_stats.items():
        #         removed_tree.add(
        #             f"{entity_type} => {entity_count} in total", guide_style="blue"
        #         )
        #
        # results_panel = Panel(epilogue_tree)
        #
        # self._console.print(results_panel)

    @property
    def is_needed(self) -> bool:
        """Whether this whole section is actually needed for rendering."""
        return self._is_needed

    async def _send_section(self, section_name: str) -> None:
        await self._websocket.send_json(
            {"type": "section", "section-name": section_name},
        )

    async def _send_status_create(
        self,
        message: str,
        entity_type: str,
        entity_id: Optional[EntityId],
        entity_name: Optional[str],
    ) -> None:
        await self._websocket.send_json(
            {
                "type": "status-create",
                "message": message,
                "entity_type": entity_type,
                "entity_id": str(entity_id) if entity_id else None,
                "entity_name": entity_name,
            },
        )

    async def _send_status_finish(
        self,
        message: str,
        entity_type: str,
        entity_id: Optional[EntityId],
        entity_name: Optional[str],
    ) -> None:
        await self._websocket.send_json(
            {
                "type": "status-finish",
                "message": message,
                "entity_type": entity_type,
                "entity_id": str(entity_id) if entity_id else None,
                "entity_name": entity_name,
            },
        )

    async def _send_status_clear(self) -> None:
        await self._websocket.send_json({"type": "status-clear"})


class WebsocketProgressReporterFactory(
    ProgressReporterFactory[AppLoggedInUseCaseContext]
):
    """A progress reporter factory that builds websocket progress reporters."""

    _web_sockets: Final[Dict[EntityId, _WebsocketHandle]]

    def __init__(self) -> None:
        """Constructor."""
        self._web_sockets = {}

    async def register_socket(
        self, websocket: WebSocket, user_ref_id: EntityId
    ) -> None:
        """Register a socket for this user."""
        if user_ref_id in self._web_sockets:
            await self._web_sockets[user_ref_id].replace_websocket(websocket)
        else:
            self._web_sockets[user_ref_id] = _WebsocketHandle.with_websocket(websocket)

    async def unregister_websocket(self, user_ref_id: EntityId) -> None:
        """Unregister a websocket for this user."""
        if user_ref_id not in self._web_sockets:
            return
        await self._web_sockets[user_ref_id].clear_websocket()

    async def unregister_all_websockets(self) -> None:
        """Unregidster all websockets for all users."""
        for web_socket_handle in self._web_sockets.values():
            await web_socket_handle.clear_websocket()
        self._web_sockets.clear()

    def new_reporter(
        self, context: AppLoggedInUseCaseContext
    ) -> ContextProgressReporter:
        """Construct a new progress reporter based on web sockets."""
        if context.user_ref_id not in self._web_sockets:
            self._web_sockets[
                context.user_ref_id
            ] = _WebsocketHandle.with_no_websocket()
        return WebsocketContextProgressReporter(
            websocket=self._web_sockets[context.user_ref_id],
            sections=[],
            created_entities_stats=defaultdict(list),
            updated_entities_stats=defaultdict(lambda: 0),
            archived_entities_stats=defaultdict(lambda: 0),
            removed_entities_stats=defaultdict(lambda: 0),
            print_indent=0,
        )
