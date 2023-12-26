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

from jupiter.core.domain.core.entity_name import EntityName
from jupiter.core.domain.named_entity_tag import NamedEntityTag
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import CrownEntity
from jupiter.core.framework.json import JSONDictType
from jupiter.core.framework.use_case import (
    ProgressReporter,
    ProgressReporterFactory,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppLoggedInUseCaseContext,
)
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


class WebsocketProgressReporter(ProgressReporter):
    """A progress reporter based on a Rich console that outputs progress to the console."""

    _websocket: Final[_WebsocketHandle]
    _sections: Final[List[str]]
    _created_entities: Final[List[CrownEntity]]
    _created_entities_stats: Final[
        DefaultDict[NamedEntityTag, List[Tuple[EntityName, EntityId]]]
    ]
    _updated_entities: Final[List[CrownEntity]]
    _updated_entities_stats: Final[DefaultDict[NamedEntityTag, int]]
    _removed_entities: Final[List[CrownEntity]]
    _removed_entities_stats: Final[DefaultDict[NamedEntityTag, int]]
    _print_indent: Final[int]

    def __init__(
        self,
        websocket: _WebsocketHandle,
        sections: List[str],
        created_entities: List[CrownEntity],
        created_entities_stats: DefaultDict[
            NamedEntityTag, List[Tuple[EntityName, EntityId]]
        ],
        updated_entities: List[CrownEntity],
        updated_entities_stats: DefaultDict[NamedEntityTag, int],
        removed_entities: List[CrownEntity],
        removed_entities_stats: DefaultDict[NamedEntityTag, int],
        print_indent: int,
    ) -> None:
        """Constructor."""
        self._websocket = websocket
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
        section_text = self._sections[0]
        for section_title in self._sections[1:]:
            section_text += " // "
            section_text += section_title
        await self._send_section(section_text)
        yield None
        self._sections.pop()

    async def mark_created(self, entity: CrownEntity) -> None:
        """Mark an entity as created."""
        self._created_entities.append(entity)
        self._created_entities_stats[NamedEntityTag.from_entity(entity)].append(
            (entity.name, entity.ref_id),
        )
        text = self._entity_to_str("creating", entity)
        await self._send_entity_line(
            text, NamedEntityTag.from_entity(entity), entity.ref_id, entity.name
        )

    async def mark_updated(self, entity: CrownEntity) -> None:
        """Mark an entity as created."""
        self._updated_entities.append(entity)
        self._updated_entities_stats[NamedEntityTag.from_entity(entity)] += 1
        text = self._entity_to_str("updating", entity)
        await self._send_entity_line(
            text, NamedEntityTag.from_entity(entity), entity.ref_id, entity.name
        )

    async def mark_removed(self, entity: CrownEntity) -> None:
        """Mark an entity as created."""
        self._removed_entities.append(entity)
        self._removed_entities_stats[NamedEntityTag.from_entity(entity)] += 1
        text = self._entity_to_str("removing", entity)
        await self._send_entity_line(
            text, NamedEntityTag.from_entity(entity), entity.ref_id, entity.name
        )

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
    def created_entities(self) -> List[CrownEntity]:
        """Created entities."""
        return self._created_entities

    @property
    def updated_entities(self) -> List[CrownEntity]:
        """Created entities."""
        return self._updated_entities

    @property
    def removed_entities(self) -> List[CrownEntity]:
        """Created entities."""
        return self._removed_entities

    def _entity_to_str(self, action_type: str, entity: CrownEntity) -> str:
        """Prepare the final string form for this one."""
        text = (
            self._print_indent * ".."
            + f"✅ Done with {action_type} {NamedEntityTag.from_entity(entity)}"
        )

        text += " "
        text += str(entity.ref_id)
        text += " "
        text += str(entity.name)

        return text

    async def _send_section(self, section_name: str) -> None:
        await self._websocket.send_json(
            {"type": "section", "section-name": section_name},
        )

    async def _send_entity_line(
        self,
        message: str,
        entity_tag: NamedEntityTag,
        entity_id: EntityId,
        entity_name: EntityName,
    ) -> None:
        await self._websocket.send_json(
            {
                "type": "entity-line",
                "message": message,
                "entity_tat": str(entity_tag),
                "entity_id": str(entity_id),
                "entity_name": str(entity_name),
            },
        )


class WebsocketProgressReporterFactory(
    ProgressReporterFactory[AppLoggedInMutationUseCaseContext]
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

    def new_reporter(self, context: AppLoggedInUseCaseContext) -> ProgressReporter:
        """Construct a new progress reporter based on web sockets."""
        if context.user_ref_id not in self._web_sockets:
            self._web_sockets[
                context.user_ref_id
            ] = _WebsocketHandle.with_no_websocket()
        return WebsocketProgressReporter(
            websocket=self._web_sockets[context.user_ref_id],
            sections=[],
            created_entities=[],
            created_entities_stats=defaultdict(list),
            updated_entities=[],
            updated_entities_stats=defaultdict(lambda: 0),
            removed_entities=[],
            removed_entities_stats=defaultdict(lambda: 0),
            print_indent=0,
        )
