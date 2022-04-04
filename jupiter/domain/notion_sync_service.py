"""Generic syncers between local and Notion."""
import logging
from dataclasses import dataclass
from typing import TypeVar, Final, Generic, Any, Optional, Iterable, List, Type, Dict, cast, Union

from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.domain.tag_name import TagName
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.entity import LeafEntity, TrunkEntity, BranchEntity, BranchTagEntity
from jupiter.framework.notion import NotionRootEntity, NotionTrunkEntity, NotionBranchEntity, NotionLeafEntity, \
    NotionBranchTagEntity
from jupiter.framework.notion_manager import ParentTrunkLeafNotionManager, NotionLeafEntityNotFoundError, \
    ParentTrunkBranchLeafNotionManager, NotionBranchEntityNotFoundError, ParentTrunkBranchLeafAndTagNotionManager

LOGGER = logging.getLogger(__name__)


TrunkType = TypeVar("TrunkType", bound=TrunkEntity)
BranchType = TypeVar("BranchType", bound=BranchEntity)
LeafType = TypeVar("LeafType", bound=LeafEntity)
BranchTagType = TypeVar("BranchTagType", bound=BranchTagEntity)
NotionParentType = TypeVar("NotionParentType", bound=Union[NotionRootEntity[Any], NotionTrunkEntity[Any]])
NotionTrunkType = TypeVar("NotionTrunkType", bound=NotionTrunkEntity[Any])
NotionBranchType = TypeVar("NotionBranchType", bound=NotionBranchEntity[Any])
NotionLeafType = TypeVar("NotionLeafType", bound=NotionLeafEntity[Any, Any, Any])
NotionBranchTagType = TypeVar("NotionBranchTagType", bound=NotionBranchTagEntity[Any])
NotionLeafUpsertExtraInfo = TypeVar("NotionLeafUpsertExtraInfo")
NotionLeafDirectExtraInfo = TypeVar('NotionLeafDirectExtraInfo')
NotionLeafInverseExtraInfo = TypeVar('NotionLeafInverseExtraInfo')


@dataclass(frozen=True)
class SyncResult(Generic[LeafType]):
    """The result of a sync."""
    all: Iterable[LeafType]
    created_locally: List[LeafType]
    modified_locally: List[LeafType]
    created_remotely: List[LeafType]
    modified_remotely: List[LeafType]
    removed_remotely: List[EntityId]


class TrunkLeafNotionSyncService(
        Generic[
            TrunkType,
            LeafType,
            NotionParentType,
            NotionTrunkType,
            NotionLeafType,
            NotionLeafUpsertExtraInfo,
            NotionLeafDirectExtraInfo,
            NotionLeafInverseExtraInfo]):
    """The service class for syncing a linked set of entities between local and Notion."""

    _trunk_type: Type[TrunkType]
    _leaf_type: Type[LeafType]
    _notion_leaf_type: Type[NotionLeafType]
    _storage_engine: Final[DomainStorageEngine]
    _notion_manager: ParentTrunkLeafNotionManager[
        NotionParentType, NotionTrunkType, NotionLeafType, NotionLeafUpsertExtraInfo]

    def __init__(
            self,
            trunk_type: Type[TrunkType],
            leaf_type: Type[LeafType],
            notion_leaf_type: Type[NotionLeafType],
            storage_engine: DomainStorageEngine,
            notion_manager: ParentTrunkLeafNotionManager[
                NotionParentType, NotionTrunkType, NotionLeafType, NotionLeafUpsertExtraInfo]) -> None:
        """Constructor."""
        self._trunk_type = trunk_type
        self._leaf_type = leaf_type
        self._notion_leaf_type = notion_leaf_type
        self._storage_engine = storage_engine
        self._notion_manager = notion_manager

    def sync(
            self,
            parent_ref_id: EntityId,
            upsert_info: NotionLeafUpsertExtraInfo,
            direct_info: NotionLeafDirectExtraInfo,
            inverse_info: NotionLeafInverseExtraInfo,
            drop_all_notion_side: bool,
            sync_even_if_not_modified: bool,
            filter_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> SyncResult[LeafType]:
        """Synchronise entities between Notion and local storage."""
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        with self._storage_engine.get_unit_of_work() as uow:
            trunk: TrunkType = uow.get_trunk_repository_for(self._trunk_type).load_by_parent(parent_ref_id)
            all_leaves = \
                uow.get_leaf_repository_for(self._leaf_type).find_all(
                    parent_ref_id=trunk.ref_id,
                    allow_archived=True,
                    filter_ref_ids=filter_ref_ids)
        all_leaves_set: Dict[EntityId, LeafType] = {v.ref_id: v for v in all_leaves}

        if not drop_all_notion_side:
            all_notion_leaves = self._notion_manager.load_all_leaves(trunk.ref_id)
            all_notion_leaves_notion_ids = set(self._notion_manager.load_all_saved_notion_ids(trunk.ref_id))
        else:
            self._notion_manager.drop_all_leaves(trunk.ref_id)
            all_notion_leaves = []
            all_notion_leaves_notion_ids = set()
        all_notion_leaves_set: Dict[EntityId, NotionLeafType] = {}

        created_locally = []
        modified_locally = []
        created_remotely = []
        modified_remotely = []
        removed_remotely = []

        # Explore Notion and apply to local
        for notion_leaf in all_notion_leaves:
            if filter_ref_ids_set is not None and notion_leaf.ref_id not in filter_ref_ids_set:
                LOGGER.info(f"Skipping '{notion_leaf.nice_name}' (id={notion_leaf.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Attempting to syncing '{notion_leaf.nice_name}' (id={notion_leaf.notion_id})")

            if notion_leaf.ref_id is None:
                new_leaf = notion_leaf.new_entity(trunk.ref_id, inverse_info)

                with self._storage_engine.get_unit_of_work() as uow:
                    new_leaf = uow.get_leaf_repository_for(self._leaf_type).create(new_leaf)

                self._notion_manager.link_local_and_notion_leaves(
                    trunk.ref_id, new_leaf.ref_id, notion_leaf.notion_id)

                notion_leaf = notion_leaf.join_with_entity(new_leaf, direct_info)
                self._notion_manager.save_leaf(trunk.ref_id, notion_leaf)

                all_leaves_set[new_leaf.ref_id] = new_leaf
                all_notion_leaves_set[new_leaf.ref_id] = notion_leaf
                created_locally.append(new_leaf)
                LOGGER.info(f"Created leaf with id={notion_leaf.ref_id} from Notion")
            elif notion_leaf.ref_id in all_leaves_set \
                    and notion_leaf.notion_id in all_notion_leaves_notion_ids:
                leaf = all_leaves_set[notion_leaf.ref_id]
                all_notion_leaves_set[notion_leaf.ref_id] = notion_leaf

                # If the leaf exists locally, we sync it with the remote:
                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified \
                            and notion_leaf.last_edited_time <= leaf.last_modified_time:
                        LOGGER.info(f"Skipping {notion_leaf.nice_name} because it was not modified")
                        continue

                    updated_leaf = notion_leaf.apply_to_entity(leaf, inverse_info)

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.get_leaf_repository_for(self._leaf_type).save(updated_leaf.entity)

                    if updated_leaf.should_modify_on_notion:
                        updated_notion_leaf = notion_leaf.join_with_entity(updated_leaf, direct_info)
                        self._notion_manager.save_leaf(trunk.ref_id, updated_notion_leaf)
                        LOGGER.info(f"Applies changes on Notion side too as {updated_notion_leaf.nice_name}")

                    all_leaves_set[notion_leaf.ref_id] = updated_leaf.entity
                    modified_locally.append(updated_leaf.entity)

                    LOGGER.info(f"Changed leaf with id={updated_leaf.entity.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified \
                            and leaf.last_modified_time <= notion_leaf.last_edited_time:
                        LOGGER.info(f"Skipping {notion_leaf.ref_id} because it was not modified")
                        continue

                    updated_notion_leaf = notion_leaf.join_with_entity(leaf, direct_info)

                    self._notion_manager.save_leaf(trunk.ref_id, updated_notion_leaf)

                    all_notion_leaves_set[notion_leaf.ref_id] = updated_notion_leaf
                    modified_remotely.append(leaf)

                    LOGGER.info(f"Changed leaf with id={notion_leaf.nice_name} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random leaf added by someone, where they completed themselves a ref_id. It's a bad
                #    setup, and we remove it.
                # 2. This is a leaf added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                try:
                    self._notion_manager.remove_leaf(trunk.ref_id, notion_leaf.ref_id)
                    removed_remotely.append(notion_leaf.ref_id)
                    LOGGER.info(f"Removed leaf with id={notion_leaf.ref_id} from Notion")
                except NotionLeafEntityNotFoundError:
                    LOGGER.info(f"Skipped dangling leaf in Notion {notion_leaf.ref_id}")

        # Explore local and apply to Notion now
        for leaf in all_leaves:
            if leaf.ref_id in all_notion_leaves_set:
                # The leaf already exists on Notion side, so it was handled by the above loop!
                continue
            if leaf.archived:
                continue

            # If the leaf does not exist on Notion side, we create it.
            notion_leaf = \
                cast(NotionLeafType, self._notion_leaf_type.new_notion_entity(cast(Any, leaf), cast(Any, direct_info)))
            self._notion_manager.upsert_leaf(trunk.ref_id, notion_leaf, upsert_info)
            all_notion_leaves_set[leaf.ref_id] = notion_leaf
            created_remotely.append(leaf)
            LOGGER.info(f"Created new leaf on Notion side {notion_leaf.nice_name}")

        return SyncResult(
            all=all_leaves_set.values(),
            created_locally=created_locally,
            modified_locally=modified_locally,
            created_remotely=created_remotely,
            modified_remotely=modified_remotely,
            removed_remotely=removed_remotely)


class TrunkBranchLeafNotionSyncService(
        Generic[
            TrunkType,
            BranchType,
            LeafType,
            NotionParentType,
            NotionTrunkType,
            NotionBranchType,
            NotionLeafType,
            NotionLeafUpsertExtraInfo,
            NotionLeafDirectExtraInfo,
            NotionLeafInverseExtraInfo]):
    """The service class for syncing a trunk branch leaf structure between local and Notion."""

    _trunk_type: Type[TrunkType]
    _branch_type: Type[BranchType]
    _leaf_type: Type[LeafType]
    _notion_branch_type: Type[NotionBranchType]
    _notion_leaf_type: Type[NotionLeafType]
    _storage_engine: Final[DomainStorageEngine]
    _notion_manager: ParentTrunkBranchLeafNotionManager[
        NotionParentType, NotionTrunkType, NotionBranchType, NotionLeafType, NotionLeafUpsertExtraInfo]

    def __init__(
            self,
            trunk_type: Type[TrunkType],
            branch_type: Type[BranchType],
            leaf_type: Type[LeafType],
            notion_branch_type: Type[NotionBranchType],
            notion_leaf_type: Type[NotionLeafType],
            storage_engine: DomainStorageEngine,
            notion_manager: ParentTrunkBranchLeafNotionManager[
                NotionParentType, NotionTrunkType, NotionBranchType, NotionLeafType,
                NotionLeafUpsertExtraInfo]) -> None:
        """Constructor."""
        self._trunk_type = trunk_type
        self._branch_type = branch_type
        self._leaf_type = leaf_type
        self._notion_branch_type = notion_branch_type
        self._notion_leaf_type = notion_leaf_type
        self._storage_engine = storage_engine
        self._notion_manager = notion_manager

    def sync(
            self,
            right_now: Timestamp,
            parent_ref_id: EntityId,
            branch: BranchType,
            upsert_info: NotionLeafUpsertExtraInfo,
            direct_info: NotionLeafDirectExtraInfo,
            inverse_info: NotionLeafInverseExtraInfo,
            drop_all_notion_side: bool,
            sync_even_if_not_modified: bool,
            filter_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> SyncResult[LeafType]:
        """Synchronize a branch and its entries between Notion and local storage."""
        with self._storage_engine.get_unit_of_work() as uow:
            trunk: TrunkType = uow.get_trunk_repository_for(self._trunk_type).load_by_parent(parent_ref_id)

        try:
            notion_branch = self._notion_manager.load_branch(trunk.ref_id, branch.ref_id)

            if sync_prefer == SyncPrefer.LOCAL:
                updated_notion_branch = notion_branch.join_with_entity(branch)
                self._notion_manager.save_branch(trunk.ref_id, updated_notion_branch)
                LOGGER.info("Applied changes to Notion")
            elif sync_prefer == SyncPrefer.NOTION:
                branch = notion_branch.apply_to_entity(branch, right_now)
                with self._storage_engine.get_unit_of_work() as uow:
                    uow.get_branch_repository_for(self._branch_type).save(branch)
                LOGGER.info("Applied local change")
            else:
                raise Exception(f"Invalid preference {sync_prefer}")
        except NotionBranchEntityNotFoundError:
            LOGGER.info("Trying to recreate the branch")
            notion_branch = cast(NotionBranchType, self._notion_branch_type.new_notion_entity(cast(Any, branch)))
            self._notion_manager.upsert_branch(trunk.ref_id, notion_branch)

        # Now synchronize the list items here.
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        with self._storage_engine.get_unit_of_work() as uow:
            all_leaves = \
                uow.get_leaf_repository_for(self._leaf_type).find_all(
                    parent_ref_id=branch.ref_id,
                    allow_archived=True,
                    filter_ref_ids=filter_ref_ids_set)
        all_leaves_set: Dict[EntityId, LeafType] = {sli.ref_id: sli for sli in all_leaves}

        if not drop_all_notion_side:
            all_notion_leaves = self._notion_manager.load_all_leaves(trunk.ref_id, branch.ref_id)
            all_notion_branch_notion_ids = \
                set(self._notion_manager.load_all_saved_notion_ids(trunk.ref_id, branch.ref_id))
        else:
            self._notion_manager.drop_all_leaves(trunk.ref_id, branch.ref_id)
            all_notion_leaves = []
            all_notion_branch_notion_ids = set()
        all_notion_leaves_set = {}

        created_locally = []
        modified_locally = []
        created_remotely = []
        modified_remotely = []
        removed_remotely = []

        # Explore Notion and apply to local
        for notion_leaf in all_notion_leaves:
            if filter_ref_ids_set is not None and notion_leaf.ref_id not in filter_ref_ids_set:
                LOGGER.info(f"Skipping '{notion_leaf.nice_name}' (id={notion_leaf.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Attempting to syncing '{notion_leaf.nice_name}' (id={notion_leaf.notion_id})")

            if notion_leaf.ref_id is None:
                # If the branch entry doesn't exist locally, we create it.
                new_leaf = notion_leaf.new_entity(branch.ref_id, None)

                with self._storage_engine.get_unit_of_work() as uow:
                    new_leaf = uow.get_leaf_repository_for(self._leaf_type).create(new_leaf)

                self._notion_manager.link_local_and_notion_leaves(
                    trunk.ref_id, branch.ref_id, new_leaf.ref_id, notion_leaf.notion_id)

                notion_leaf = notion_leaf.join_with_entity(new_leaf, None)
                self._notion_manager.save_leaf(trunk.ref_id, branch.ref_id, notion_leaf)

                all_leaves_set[new_leaf.ref_id] = new_leaf
                all_notion_leaves_set[new_leaf.ref_id] = notion_leaf
                created_locally.append(new_leaf)
                LOGGER.info(f"Created leaf with id={notion_leaf.ref_id} from Notion")
            elif notion_leaf.ref_id in all_leaves_set and \
                    notion_leaf.notion_id in all_notion_branch_notion_ids:
                leaf = all_leaves_set[notion_leaf.ref_id]
                all_notion_leaves_set[notion_leaf.ref_id] = notion_leaf

                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified and \
                            notion_leaf.last_edited_time <= leaf.last_modified_time:
                        LOGGER.info(f"Skipping {notion_leaf.nice_name} because it was not modified")
                        continue

                    updated_leaf = notion_leaf.apply_to_entity(leaf, inverse_info)

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.get_leaf_repository_for(self._leaf_type).save(updated_leaf.entity)

                    if updated_leaf.should_modify_on_notion:
                        updated_notion_leaf = notion_leaf.join_with_entity(updated_leaf, direct_info)
                        self._notion_manager.save_leaf(trunk.ref_id, branch.ref_id, updated_notion_leaf)
                        LOGGER.info(f"Applies changes on Notion side too as {updated_notion_leaf.nice_name}")

                    all_leaves_set[notion_leaf.ref_id] = updated_leaf.entity
                    modified_locally.append(updated_leaf.entity)

                    LOGGER.info(f"Changed leaf with id={updated_leaf.entity.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified and \
                            leaf.last_modified_time <= notion_leaf.last_edited_time:
                        LOGGER.info(f"Skipping {notion_leaf.ref_id} because it was not modified")
                        continue

                    updated_notion_leaf = notion_leaf.join_with_entity(leaf, direct_info)

                    self._notion_manager.save_leaf(trunk.ref_id, branch.ref_id, updated_notion_leaf)

                    all_notion_leaves_set[notion_leaf.ref_id] = updated_notion_leaf
                    modified_remotely.append(leaf)

                    LOGGER.info(f"Changed leaf with id={notion_leaf.nice_name} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random branch entry added by someone, where they completed themselves a ref_id.
                #    It's a bad setup, and we remove it.
                # 2. This is a branch entry added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                try:
                    self._notion_manager.remove_leaf(trunk.ref_id, branch.ref_id, notion_leaf.ref_id)
                    removed_remotely.append(notion_leaf.ref_id)
                    LOGGER.info(f"Removed leaf with id={notion_leaf.ref_id} from Notion")
                except NotionLeafEntityNotFoundError:
                    LOGGER.info(f"Skipped dangling leaf in Notion {notion_leaf.ref_id}")

        for leaf in all_leaves:
            if leaf.ref_id in all_notion_leaves_set:
                # The branch entry already exists on Notion side, so it was handled by the above loop!
                continue
            if leaf.archived:
                continue

            # If the branch entry does not exist on Notion side, we create it.
            notion_leaf = \
                cast(NotionLeafType, self._notion_leaf_type.new_notion_entity(cast(Any, leaf), cast(Any, direct_info)))
            self._notion_manager.upsert_leaf(trunk.ref_id, branch.ref_id, notion_leaf, upsert_info)
            all_notion_leaves_set[leaf.ref_id] = notion_leaf
            created_remotely.append(leaf)
            LOGGER.info(f"Created new leaf on Notion side {notion_leaf.nice_name}")

        return SyncResult(
            all=all_leaves_set.values(),
            created_locally=created_locally,
            modified_locally=modified_locally,
            created_remotely=created_remotely,
            modified_remotely=modified_remotely,
            removed_remotely=removed_remotely)


@dataclass(frozen=True)
class _NotionBranchLeafAndTagDirectInfo(Generic[BranchTagType]):
    """Extra info for the app to Notion copy."""
    tags_by_ref_id: Dict[EntityId, BranchTagType]


@dataclass(frozen=True)
class _NotionBranchLeafAndTagInverseInfo(Generic[BranchTagType]):
    """Extra info for the Notion to app copy."""
    tags_by_name: Dict[TagName, BranchTagType]


class TrunkBranchLeafAndTagNotionSyncService(
        Generic[
            TrunkType,
            BranchType,
            LeafType,
            BranchTagType,
            NotionParentType,
            NotionTrunkType,
            NotionBranchType,
            NotionLeafType,
            NotionBranchTagType,
            NotionLeafUpsertExtraInfo]):
    """The service class for syncing a trunk branch leaf structure between local and Notion."""

    _trunk_type: Type[TrunkType]
    _branch_type: Type[BranchType]
    _leaf_type: Type[LeafType]
    _branch_tag_type: Type[BranchTagType]
    _notion_branch_type: Type[NotionBranchType]
    _notion_leaf_type: Type[NotionLeafType]
    _notion_branch_tag_type: Type[NotionBranchTagType]
    _storage_engine: Final[DomainStorageEngine]
    _notion_manager: ParentTrunkBranchLeafAndTagNotionManager[
        NotionParentType, NotionTrunkType, NotionBranchType, NotionLeafType, NotionBranchTagType,
        NotionLeafUpsertExtraInfo]

    def __init__(
            self,
            trunk_type: Type[TrunkType],
            branch_type: Type[BranchType],
            leaf_type: Type[LeafType],
            branch_tag_type: Type[BranchTagType],
            notion_branch_type: Type[NotionBranchType],
            notion_leaf_type: Type[NotionLeafType],
            notion_branch_tag_type: Type[NotionBranchTagType],
            storage_engine: DomainStorageEngine,
            notion_manager: ParentTrunkBranchLeafAndTagNotionManager[
                NotionParentType, NotionTrunkType, NotionBranchType, NotionLeafType, NotionBranchTagType,
                NotionLeafUpsertExtraInfo]) -> None:
        """Constructor."""
        self._trunk_type = trunk_type
        self._branch_type = branch_type
        self._leaf_type = leaf_type
        self._branch_tag_type = branch_tag_type
        self._notion_branch_type = notion_branch_type
        self._notion_leaf_type = notion_leaf_type
        self._notion_branch_tag_type = notion_branch_tag_type
        self._storage_engine = storage_engine
        self._notion_manager = notion_manager

    def sync(
            self,
            right_now: Timestamp,
            parent_ref_id: EntityId,
            branch: BranchType,
            upsert_info: NotionLeafUpsertExtraInfo,
            drop_all_notion_side: bool,
            sync_even_if_not_modified: bool,
            filter_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> SyncResult[LeafType]:
        """Synchronize a branch and its entries between Notion and local storage."""
        with self._storage_engine.get_unit_of_work() as uow:
            trunk: TrunkType = uow.get_trunk_repository_for(self._trunk_type).load_by_parent(parent_ref_id)

        try:
            notion_branch = self._notion_manager.load_branch(trunk.ref_id, branch.ref_id)

            if sync_prefer == SyncPrefer.LOCAL:
                updated_notion_branch = notion_branch.join_with_entity(branch)
                self._notion_manager.save_branch(trunk.ref_id, updated_notion_branch)
                LOGGER.info("Applied changes to Notion")
            elif sync_prefer == SyncPrefer.NOTION:
                branch = notion_branch.apply_to_entity(branch, right_now)
                with self._storage_engine.get_unit_of_work() as uow:
                    uow.get_branch_repository_for(self._branch_type).save(branch)
                LOGGER.info("Applied local change")
            else:
                raise Exception(f"Invalid preference {sync_prefer}")
        except NotionBranchEntityNotFoundError:
            LOGGER.info("Trying to recreate the branch")
            notion_branch = cast(NotionBranchType, self._notion_branch_type.new_notion_entity(cast(Any, branch)))
            self._notion_manager.upsert_branch(trunk.ref_id, notion_branch)

        # Sync the tags
        with self._storage_engine.get_unit_of_work() as uow:
            all_branch_tags = \
                uow.get_leaf_repository_for(self._branch_tag_type)\
                    .find_all(parent_ref_id=branch.ref_id, allow_archived=True)
        all_branch_tags_set = {slt.ref_id: slt for slt in all_branch_tags}
        all_branch_tags_by_name = {slt.tag_name: slt for slt in all_branch_tags}

        if not drop_all_notion_side:
            all_notion_branch_tags = self._notion_manager.load_all_branch_tags(trunk.ref_id, branch.ref_id)
            all_notion_branch_tags_notion_ids = \
                set(self._notion_manager.load_all_saved_branch_tags_notion_ids(trunk.ref_id, branch.ref_id))
        else:
            self._notion_manager.drop_all_branch_tags(trunk.ref_id, branch.ref_id)
            all_notion_branch_tags = []
            all_notion_branch_tags_notion_ids = set()
        notion_branch_tags_set = {}

        for notion_branch_tag in all_notion_branch_tags:
            LOGGER.info(f"Syncing tag '{notion_branch_tag.nice_name}' (id={notion_branch_tag.notion_id})")

            if notion_branch_tag.ref_id is None:
                # If the branch tag doesn't exist locally, we create it.
                new_branch_tag = notion_branch_tag.new_entity(branch.ref_id)
                with self._storage_engine.get_unit_of_work() as uow:
                    new_branch_tag = uow.get_leaf_repository_for(self._branch_tag_type).create(new_branch_tag)

                self._notion_manager.link_local_and_notion_branch_tags(
                    trunk.ref_id, branch.ref_id, new_branch_tag.ref_id, notion_branch_tag.notion_id)

                notion_branch_tag = notion_branch_tag.join_with_entity(new_branch_tag)
                self._notion_manager.save_branch_tag(trunk.ref_id, branch.ref_id, notion_branch_tag)

                notion_branch_tags_set[new_branch_tag.ref_id] = notion_branch_tag
                all_branch_tags.append(new_branch_tag)
                all_branch_tags_set[new_branch_tag.ref_id] = new_branch_tag
                all_branch_tags_by_name[new_branch_tag.tag_name] = new_branch_tag
                LOGGER.info(f"Created branch tag with id={notion_branch_tag.ref_id} from Notion")
            elif notion_branch_tag.ref_id in all_branch_tags_set and \
                    notion_branch_tag.notion_id in all_notion_branch_tags_notion_ids:
                branch_tag = all_branch_tags_set[notion_branch_tag.ref_id]
                notion_branch_tags_set[notion_branch_tag.ref_id] = notion_branch_tag

                if sync_prefer == SyncPrefer.NOTION:
                    updated_branch_tag = notion_branch_tag.apply_to_entity(branch_tag)
                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.get_leaf_repository_for(self._branch_tag_type).save(updated_branch_tag.entity)
                    all_branch_tags_set[notion_branch_tag.ref_id] = updated_branch_tag.entity
                    all_branch_tags_by_name[branch_tag.tag_name] = updated_branch_tag.entity

                    LOGGER.info(f"Changed branch tag with id={updated_branch_tag.entity.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    updated_notion_branch_tag = notion_branch_tag.join_with_entity(branch_tag)
                    self._notion_manager.save_branch_tag(trunk.ref_id, branch.ref_id, updated_notion_branch_tag)
                    LOGGER.info(f"Changed branch tag with id={notion_branch_tag.ref_id} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random branch tag added by someone, where they completed themselves a ref_id.
                #    It's a bad setup, and we remove it.
                # 2. This is a smart list item added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                try:
                    self._notion_manager.remove_branch_tag(trunk.ref_id, branch.ref_id, notion_branch_tag.ref_id)
                    LOGGER.info(f"Removed branch tag with id={notion_branch_tag.ref_id} from Notion")
                except NotionLeafEntityNotFoundError:
                    LOGGER.info(f"Skipped dangling branch tag in Notion {notion_branch_tag.ref_id}")

        for branch_tag in all_branch_tags:
            if branch_tag.ref_id in notion_branch_tags_set:
                # The smart list item already exists on Notion side, so it was handled by the above loop!
                continue
            if branch_tag.archived:
                continue

            # If the smart list item does not exist on Notion side, we create it.
            notion_branch_tag = \
                cast(NotionBranchTagType, self._notion_branch_tag_type.new_notion_entity(cast(Any, branch_tag)))
            self._notion_manager.upsert_branch_tag(trunk.ref_id, branch.ref_id, notion_branch_tag)
            LOGGER.info(f"Created new branch tag on Notion side '{branch_tag.ref_id}'")

        # Now synchronize the list items here.
        filter_ref_ids_set = frozenset(filter_ref_ids) if filter_ref_ids else None

        with self._storage_engine.get_unit_of_work() as uow:
            all_leaves = \
                uow.get_leaf_repository_for(self._leaf_type).find_all(
                    parent_ref_id=branch.ref_id,
                    allow_archived=True,
                    filter_ref_ids=filter_ref_ids_set)
        all_leaves_set: Dict[EntityId, LeafType] = {sli.ref_id: sli for sli in all_leaves}

        if not drop_all_notion_side:
            all_notion_leaves = self._notion_manager.load_all_leaves(trunk.ref_id, branch.ref_id)
            all_notion_branch_notion_ids = \
                set(self._notion_manager.load_all_saved_notion_ids(trunk.ref_id, branch.ref_id))
        else:
            self._notion_manager.drop_all_leaves(trunk.ref_id, branch.ref_id)
            all_notion_leaves = []
            all_notion_branch_notion_ids = set()
        all_notion_leaves_set = {}

        direct_info = _NotionBranchLeafAndTagDirectInfo(tags_by_ref_id=all_branch_tags_set)
        inverse_info = _NotionBranchLeafAndTagInverseInfo(tags_by_name=all_branch_tags_by_name)

        created_locally = []
        modified_locally = []
        created_remotely = []
        modified_remotely = []
        removed_remotely = []

        # Explore Notion and apply to local
        for notion_leaf in all_notion_leaves:
            if filter_ref_ids_set is not None and notion_leaf.ref_id not in filter_ref_ids_set:
                LOGGER.info(f"Skipping '{notion_leaf.nice_name}' (id={notion_leaf.notion_id}) because of filtering")
                continue

            LOGGER.info(f"Attempting to syncing '{notion_leaf.nice_name}' (id={notion_leaf.notion_id})")

            if notion_leaf.ref_id is None:
                # If the branch entry doesn't exist locally, we create it.
                new_leaf = notion_leaf.new_entity(branch.ref_id, None)

                with self._storage_engine.get_unit_of_work() as uow:
                    new_leaf = uow.get_leaf_repository_for(self._leaf_type).create(new_leaf)

                self._notion_manager.link_local_and_notion_leaves(
                    trunk.ref_id, branch.ref_id, new_leaf.ref_id, notion_leaf.notion_id)

                notion_leaf = notion_leaf.join_with_entity(new_leaf, None)
                self._notion_manager.save_leaf(trunk.ref_id, branch.ref_id, notion_leaf)

                all_leaves_set[new_leaf.ref_id] = new_leaf
                all_notion_leaves_set[new_leaf.ref_id] = notion_leaf
                created_locally.append(new_leaf)
                LOGGER.info(f"Created leaf with id={notion_leaf.ref_id} from Notion")
            elif notion_leaf.ref_id in all_leaves_set and \
                    notion_leaf.notion_id in all_notion_branch_notion_ids:
                leaf = all_leaves_set[notion_leaf.ref_id]
                all_notion_leaves_set[notion_leaf.ref_id] = notion_leaf

                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified and \
                            notion_leaf.last_edited_time <= leaf.last_modified_time:
                        LOGGER.info(f"Skipping {notion_leaf.nice_name} because it was not modified")
                        continue

                    updated_leaf = notion_leaf.apply_to_entity(leaf, inverse_info)

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.get_leaf_repository_for(self._leaf_type).save(updated_leaf.entity)

                    if updated_leaf.should_modify_on_notion:
                        updated_notion_leaf = notion_leaf.join_with_entity(updated_leaf, direct_info)
                        self._notion_manager.save_leaf(trunk.ref_id, branch.ref_id, updated_notion_leaf)
                        LOGGER.info(f"Applies changes on Notion side too as {updated_notion_leaf.nice_name}")

                    all_leaves_set[notion_leaf.ref_id] = updated_leaf.entity
                    modified_locally.append(updated_leaf.entity)

                    LOGGER.info(f"Changed leaf with id={updated_leaf.entity.ref_id} from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified and \
                            leaf.last_modified_time <= notion_leaf.last_edited_time:
                        LOGGER.info(f"Skipping {notion_leaf.ref_id} because it was not modified")
                        continue

                    updated_notion_leaf = notion_leaf.join_with_entity(leaf, direct_info)

                    self._notion_manager.save_leaf(trunk.ref_id, branch.ref_id, updated_notion_leaf)

                    all_notion_leaves_set[notion_leaf.ref_id] = updated_notion_leaf
                    modified_remotely.append(leaf)

                    LOGGER.info(f"Changed leaf with id={notion_leaf.nice_name} from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random branch entry added by someone, where they completed themselves a ref_id.
                #    It's a bad setup, and we remove it.
                # 2. This is a branch entry added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                try:
                    self._notion_manager.remove_leaf(trunk.ref_id, branch.ref_id, notion_leaf.ref_id)
                    removed_remotely.append(notion_leaf.ref_id)
                    LOGGER.info(f"Removed leaf with id={notion_leaf.ref_id} from Notion")
                except NotionLeafEntityNotFoundError:
                    LOGGER.info(f"Skipped dangling leaf in Notion {notion_leaf.ref_id}")

        for leaf in all_leaves:
            if leaf.ref_id in all_notion_leaves_set:
                # The branch entry already exists on Notion side, so it was handled by the above loop!
                continue
            if leaf.archived:
                continue

            # If the branch entry does not exist on Notion side, we create it.
            notion_leaf =\
                cast(NotionLeafType, self._notion_leaf_type.new_notion_entity(cast(Any, leaf), cast(Any, direct_info)))
            self._notion_manager.upsert_leaf(trunk.ref_id, branch.ref_id, notion_leaf, upsert_info)
            all_notion_leaves_set[leaf.ref_id] = notion_leaf
            created_remotely.append(leaf)
            LOGGER.info(f"Created new leaf on Notion side {notion_leaf.nice_name}")

        return SyncResult(
            all=all_leaves_set.values(),
            created_locally=created_locally,
            modified_locally=modified_locally,
            created_remotely=created_remotely,
            modified_remotely=modified_remotely,
            removed_remotely=removed_remotely)
