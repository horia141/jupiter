"""Framework-level types of Notion managers."""
import abc
from typing import TypeVar, Any, Generic, Iterable, Optional, Union

from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.notion import NotionRootEntity, NotionTrunkEntity, NotionLeafEntity, NotionBranchEntity, \
    NotionBranchTagEntity

ParentType = TypeVar("ParentType", bound=Union[NotionRootEntity[Any], NotionTrunkEntity[Any]])
TrunkType = TypeVar("TrunkType", bound=NotionTrunkEntity[Any])
BranchType = TypeVar("BranchType", bound=NotionBranchEntity[Any])
LeafType = TypeVar("LeafType", bound=NotionLeafEntity[Any, Any, Any])
BranchTagType = TypeVar("BranchTagType", bound=NotionBranchTagEntity[Any])
LeafExtraInfoType = TypeVar("LeafExtraInfoType")


class NotionBranchEntityNotFoundError(Exception):
    """Exception raised when a particular Notion branch is not found."""


class NotionLeafEntityNotFoundError(Exception):
    """Exception raised when a particular Notion leaf is not found."""


class NotionManager(Generic[ParentType, TrunkType], abc.ABC):
    """A manager of Notion entities."""

    @abc.abstractmethod
    def upsert_trunk(self, parent: ParentType, trunk: TrunkType) -> None:
        """Upsert the root page structure for leafs."""


class ParentTrunkLeafNotionManager(
        Generic[ParentType, TrunkType, LeafType, LeafExtraInfoType], NotionManager[ParentType, TrunkType], abc.ABC):
    """A manager for an entity structure consisting of a parent (a root or trunk) and a trunk with various leafs."""

    @abc.abstractmethod
    def upsert_leaf(self, trunk_ref_id: EntityId, leaf: LeafType, extra_info: LeafExtraInfoType) -> LeafType:
        """Upsert a leaf on Notion-side."""

    @abc.abstractmethod
    def save_leaf(
            self, trunk_ref_id: EntityId, leaf: LeafType, extra_info: Optional[LeafExtraInfoType] = None) -> LeafType:
        """Upsert a leaf on Notion-side."""

    @abc.abstractmethod
    def load_leaf(self, trunk_ref_id: EntityId, leaf_ref_id: EntityId) -> LeafType:
        """Load a Notion-side leaf."""

    @abc.abstractmethod
    def load_all_leaves(self, trunk_ref_id: EntityId) -> Iterable[LeafType]:
        """Load all Notion-side leafs."""

    @abc.abstractmethod
    def remove_leaf(self, trunk_ref_id: EntityId, leaf_ref_id: EntityId) -> None:
        """Remove a leaf on Notion-side."""

    @abc.abstractmethod
    def drop_all_leaves(self, trunk_ref_id: EntityId) -> None:
        """Remove all leafs on Notion-side."""

    @abc.abstractmethod
    def load_all_saved_ref_ids(self, trunk_ref_id: EntityId) -> Iterable[EntityId]:
        """Load ids of all persons we know about from Notion side."""

    @abc.abstractmethod
    def load_all_saved_notion_ids(self, trunk_ref_id: EntityId) -> Iterable[NotionId]:
        """Load ids of all leafs we know about from Notion side."""

    @abc.abstractmethod
    def link_local_and_notion_leaves(self, trunk_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local and Notion version of the entities."""


class ParentTrunkBranchLeafNotionManager(
        Generic[ParentType, TrunkType, BranchType, LeafType, LeafExtraInfoType],
        NotionManager[ParentType, TrunkType],
        abc.ABC):
    """A manager for an entity structure consisting of a parent, a trunk with many branches and leaves."""

    @abc.abstractmethod
    def upsert_branch(self, trunk_ref_id: EntityId, branch: BranchType) -> BranchType:
        """Upsert a branch on Notion-side."""

    @abc.abstractmethod
    def save_branch(self, trunk_ref_id: EntityId, branch: BranchType) -> BranchType:
        """Load a branch on Notion-side."""

    @abc.abstractmethod
    def load_branch(self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> BranchType:
        """Load a branch on Notion-side."""

    @abc.abstractmethod
    def remove_branch(self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> None:
        """Remove a branch on Notion-side."""

    @abc.abstractmethod
    def upsert_leaf(
            self, trunk_ref_id: EntityId, branch_ref_id: EntityId, leaf: LeafType,
            extra_info: LeafExtraInfoType) -> LeafType:
        """Upsert a branch leaf on Notion-side."""

    @abc.abstractmethod
    def save_leaf(
            self, trunk_ref_id: EntityId, branch_ref_id: EntityId, leaf: LeafType,
            extra_info: Optional[LeafExtraInfoType] = None) -> LeafType:
        """Save an already existing branch leaf on Notion-side."""

    @abc.abstractmethod
    def load_leaf(
            self, trunk_ref_id: EntityId, branch_ref_id: EntityId, leaf_ref_id: EntityId) -> LeafType:
        """Load a particular branch leaf."""

    @abc.abstractmethod
    def load_all_leaves(
            self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> Iterable[LeafType]:
        """Load all branch leaves."""

    @abc.abstractmethod
    def remove_leaf(self, trunk_ref_id: EntityId, branch_ref_id: EntityId, leaf_ref_id: EntityId) -> None:
        """Remove a branch on Notion-side."""

    @abc.abstractmethod
    def drop_all_leaves(self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> None:
        """Remove all branch leaves Notion-side."""

    @abc.abstractmethod
    def load_all_saved_ref_ids(self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the branch leaves."""

    @abc.abstractmethod
    def load_all_saved_notion_ids(self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion ids for the branch leaves."""

    @abc.abstractmethod
    def link_local_and_notion_leaves(
            self, trunk_ref_id: EntityId, branch_ref_id: EntityId, leaf_ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""


class ParentTrunkBranchLeafAndTagNotionManager(
        Generic[ParentType, TrunkType, BranchType, LeafType, BranchTagType, LeafExtraInfoType],
        ParentTrunkBranchLeafNotionManager[ParentType, TrunkType, BranchType, LeafType, LeafExtraInfoType],
        abc.ABC):
    """A manager for an entity structure consisting of a parent, a trunk with many branches and leaves and tags."""

    @abc.abstractmethod
    def upsert_branch_tag(
            self, trunk_ref_id: EntityId, branch_ref_id: EntityId, branch_tag: BranchTagType) -> BranchTagType:
        """Upsert a branch tag on Notion-side."""

    @abc.abstractmethod
    def save_branch_tag(
            self, trunk_ref_id: EntityId, branch_ref_id: EntityId, branch_tag: BranchTagType) -> BranchTagType:
        """Update the Notion-side branch tag with new data."""

    @abc.abstractmethod
    def load_branch_tag(self, trunk_ref_id: EntityId, branch_ref_id: EntityId, ref_id: EntityId) -> BranchTagType:
        """Retrieve all the Notion-side branch tags."""

    @abc.abstractmethod
    def load_all_branch_tags(self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> Iterable[BranchTagType]:
        """Retrieve all the Notion-side branch tags."""

    @abc.abstractmethod
    def remove_branch_tag(
            self, trunk_ref_id: EntityId, branch_ref_id: EntityId, branch_tag_ref_id: Optional[EntityId]) -> None:
        """Remove a branch tag on Notion-side."""

    @abc.abstractmethod
    def drop_all_branch_tags(self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> None:
        """Remove all branch tags Notion-side."""

    @abc.abstractmethod
    def load_all_saved_branch_tags_notion_ids(
            self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the Notion ids for the branch tags."""

    @abc.abstractmethod
    def link_local_and_notion_branch_tags(
            self, trunk_ref_id: EntityId, branch_ref_id: EntityId, branch_tag_ref_id: EntityId,
            notion_id: NotionId) -> None:
        """Link a local tag with the Notion one, useful in syncing processes."""
