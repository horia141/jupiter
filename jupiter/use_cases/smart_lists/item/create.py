"""The command for creating a smart list item."""
from dataclasses import dataclass
from typing import Optional, Final, List

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import (
    SmartListNotionManager,
)
from jupiter.domain.smart_lists.notion_smart_list_item import NotionSmartListItem
from jupiter.domain.smart_lists.notion_smart_list_tag import NotionSmartListTag
from jupiter.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.domain.smart_lists.smart_list_item_name import SmartListItemName
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.url import URL
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
    ProgressReporter,
)
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
from jupiter.utils.time_provider import TimeProvider


class SmartListItemCreateUseCase(
    AppMutationUseCase["SmartListItemCreateUseCase.Args", None]
):
    """The command for creating a smart list item."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        smart_list_key: SmartListKey
        name: SmartListItemName
        is_done: bool
        tag_names: List[SmartListTagName]
        url: Optional[URL]

    _smart_list_notion_manager: Final[SmartListNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        smart_list_notion_manager: SmartListNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._smart_list_notion_manager = smart_list_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            smart_list_collection = uow.smart_list_collection_repository.load_by_parent(
                workspace.ref_id
            )
            smart_list = uow.smart_list_repository.load_by_key(
                smart_list_collection.ref_id, args.smart_list_key
            )
            smart_list_tags = {
                t.tag_name: t
                for t in uow.smart_list_tag_repository.find_all_with_filters(
                    parent_ref_id=smart_list.ref_id, filter_tag_names=args.tag_names
                )
            }

        for tag_name in args.tag_names:
            if tag_name in smart_list_tags:
                continue

            with progress_reporter.start_creating_entity(
                "smart list tag", str(tag_name)
            ) as entity_reporter:
                with self._storage_engine.get_unit_of_work() as uow:
                    smart_list_tag = SmartListTag.new_smart_list_tag(
                        smart_list_ref_id=smart_list.ref_id,
                        tag_name=tag_name,
                        source=EventSource.CLI,
                        created_time=self._time_provider.get_current_time(),
                    )
                    smart_list_tag = uow.smart_list_tag_repository.create(
                        smart_list_tag
                    )
                    entity_reporter.mark_known_entity_id(
                        smart_list_tag.ref_id
                    ).mark_local_change()
                    smart_list_tags[smart_list_tag.tag_name] = smart_list_tag

                notion_smart_list_tag = NotionSmartListTag.new_notion_entity(
                    smart_list_tag
                )
                self._smart_list_notion_manager.upsert_branch_tag(
                    smart_list_collection.ref_id,
                    smart_list.ref_id,
                    notion_smart_list_tag,
                )
                entity_reporter.mark_remote_change()

        with progress_reporter.start_creating_entity(
            "smart list item", str(args.name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                smart_list_item = SmartListItem.new_smart_list_item(
                    archived=False,
                    smart_list_ref_id=smart_list.ref_id,
                    name=args.name,
                    is_done=args.is_done,
                    tags_ref_id=[t.ref_id for t in smart_list_tags.values()],
                    url=args.url,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time(),
                )
                smart_list_item = uow.smart_list_item_repository.create(smart_list_item)
                entity_reporter.mark_known_entity_id(
                    smart_list_item.ref_id
                ).mark_local_change()

            notion_smart_list_item = NotionSmartListItem.new_notion_entity(
                smart_list_item,
                NotionSmartListItem.DirectInfo(
                    {t.ref_id: t for t in smart_list_tags.values()}
                ),
            )
            self._smart_list_notion_manager.upsert_leaf(
                smart_list_collection.ref_id,
                smart_list.ref_id,
                notion_smart_list_item,
            )
            entity_reporter.mark_remote_change()
