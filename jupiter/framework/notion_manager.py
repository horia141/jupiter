"""Framework-level types of Notion managers."""
import abc
from typing import TypeVar, Any, Generic, Iterable, Optional, Union

from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.notion import (
    NotionRootEntity,
    NotionTrunkEntity,
    NotionLeafEntity,
    NotionBranchEntity,
    NotionBranchTagEntity,
)

ParentT = TypeVar("ParentT", bound=Union[NotionRootEntity[Any], NotionTrunkEntity[Any]])
TrunkT = TypeVar("TrunkT", bound=NotionTrunkEntity[Any])
BranchT = TypeVar("BranchT", bound=NotionBranchEntity[Any])
LeafT = TypeVar("LeafT", bound=NotionLeafEntity[Any, Any, Any])
BranchTagT = TypeVar("BranchTagT", bound=NotionBranchTagEntity[Any])


class NotionBranchEntityNotFoundError(Exception):
    """Exception raised when a particular Notion branch is not found."""


class NotionLeafEntityNotFoundError(Exception):
    """Exception raised when a particular Notion leaf is not found."""


class NotionManager(Generic[ParentT, TrunkT], abc.ABC):
    """A manager of Notion entities."""

    @abc.abstractmethod
    def upsert_trunk(self, parent: ParentT, trunk: TrunkT) -> None:
        """Upsert the root page structure for leafs."""


class ParentTrunkLeafNotionManager(
    Generic[ParentT, TrunkT, LeafT],
    NotionManager[ParentT, TrunkT],
    abc.ABC,
):
    """A manager for an entity structure consisting of a parent (a root or trunk) and a trunk with various leafs."""

    @abc.abstractmethod
    def upsert_leaf(self, trunk_ref_id: EntityId, leaf: LeafT) -> LeafT:
        """Upsert a leaf on Notion-side."""

    @abc.abstractmethod
    def save_leaf(self, trunk_ref_id: EntityId, leaf: LeafT) -> LeafT:
        """Upsert a leaf on Notion-side."""

    @abc.abstractmethod
    def load_leaf(self, trunk_ref_id: EntityId, leaf_ref_id: EntityId) -> LeafT:
        """Load a Notion-side leaf."""

    @abc.abstractmethod
    def load_all_leaves(self, trunk_ref_id: EntityId) -> Iterable[LeafT]:
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
    def link_local_and_notion_leaves(
        self, trunk_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId
    ) -> None:
        """Link a local and Notion version of the entities."""


class ParentTrunkBranchLeafNotionManager(
    Generic[ParentT, TrunkT, BranchT, LeafT],
    NotionManager[ParentT, TrunkT],
    abc.ABC,
):
    """A manager for an entity structure consisting of a parent, a trunk with many branches and leaves."""

    @abc.abstractmethod
    def upsert_branch(self, trunk_ref_id: EntityId, branch: BranchT) -> BranchT:
        """Upsert a branch on Notion-side."""

    @abc.abstractmethod
    def save_branch(self, trunk_ref_id: EntityId, branch: BranchT) -> BranchT:
        """Load a branch on Notion-side."""

    @abc.abstractmethod
    def load_branch(self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> BranchT:
        """Load a branch on Notion-side."""

    @abc.abstractmethod
    def remove_branch(self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> None:
        """Remove a branch on Notion-side."""

    @abc.abstractmethod
    def upsert_leaf(
        self,
        trunk_ref_id: EntityId,
        branch_ref_id: EntityId,
        leaf: LeafT,
    ) -> LeafT:
        """Upsert a branch leaf on Notion-side."""

    @abc.abstractmethod
    def save_leaf(
        self,
        trunk_ref_id: EntityId,
        branch_ref_id: EntityId,
        leaf: LeafT,
    ) -> LeafT:
        """Save an already existing branch leaf on Notion-side."""

    @abc.abstractmethod
    def load_leaf(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId, leaf_ref_id: EntityId
    ) -> LeafT:
        """Load a particular branch leaf."""

    @abc.abstractmethod
    def load_all_leaves(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId
    ) -> Iterable[LeafT]:
        """Load all branch leaves."""

    @abc.abstractmethod
    def remove_leaf(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId, leaf_ref_id: EntityId
    ) -> None:
        """Remove a branch on Notion-side."""

    @abc.abstractmethod
    def drop_all_leaves(self, trunk_ref_id: EntityId, branch_ref_id: EntityId) -> None:
        """Remove all branch leaves Notion-side."""

    @abc.abstractmethod
    def load_all_saved_ref_ids(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId
    ) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the branch leaves."""

    @abc.abstractmethod
    def load_all_saved_notion_ids(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId
    ) -> Iterable[NotionId]:
        """Retrieve all the saved Notion ids for the branch leaves."""

    @abc.abstractmethod
    def link_local_and_notion_leaves(
        self,
        trunk_ref_id: EntityId,
        branch_ref_id: EntityId,
        leaf_ref_id: EntityId,
        notion_id: NotionId,
    ) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""


class ParentTrunkBranchLeafAndTagNotionManager(
    Generic[ParentT, TrunkT, BranchT, LeafT, BranchTagT],
    ParentTrunkBranchLeafNotionManager[ParentT, TrunkT, BranchT, LeafT],
    abc.ABC,
):
    """A manager for an entity structure consisting of a parent, a trunk with many branches and leaves and tags."""

    @abc.abstractmethod
    def upsert_branch_tag(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId, branch_tag: BranchTagT
    ) -> BranchTagT:
        """Upsert a branch tag on Notion-side."""

    @abc.abstractmethod
    def save_branch_tag(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId, branch_tag: BranchTagT
    ) -> BranchTagT:
        """Update the Notion-side branch tag with new data."""

    @abc.abstractmethod
    def load_branch_tag(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId, ref_id: EntityId
    ) -> BranchTagT:
        """Retrieve all the Notion-side branch tags."""

    @abc.abstractmethod
    def load_all_branch_tags(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId
    ) -> Iterable[BranchTagT]:
        """Retrieve all the Notion-side branch tags."""

    @abc.abstractmethod
    def remove_branch_tag(
        self,
        trunk_ref_id: EntityId,
        branch_ref_id: EntityId,
        branch_tag_ref_id: Optional[EntityId],
    ) -> None:
        """Remove a branch tag on Notion-side."""

    @abc.abstractmethod
    def drop_all_branch_tags(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId
    ) -> None:
        """Remove all branch tags Notion-side."""

    @abc.abstractmethod
    def load_all_saved_branch_tags_notion_ids(
        self, trunk_ref_id: EntityId, branch_ref_id: EntityId
    ) -> Iterable[NotionId]:
        """Retrieve all the Notion ids for the branch tags."""

    @abc.abstractmethod
    def link_local_and_notion_branch_tags(
        self,
        trunk_ref_id: EntityId,
        branch_ref_id: EntityId,
        branch_tag_ref_id: EntityId,
        notion_id: NotionId,
    ) -> None:
        """Link a local tag with the Notion one, useful in syncing processes."""
