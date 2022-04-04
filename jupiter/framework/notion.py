"""Framework level elements for the Notion concepts."""
import dataclasses
from dataclasses import dataclass
from typing import Any, Optional, Generic, TypeVar, cast

from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.entity import LeafEntity, TrunkEntity, BranchEntity, RootEntity, BranchTagEntity

RootEntityT = TypeVar('RootEntityT', bound=RootEntity)
_NotionRootEntitySubclassT = TypeVar('_NotionRootEntitySubclassT', bound='NotionRootEntity[Any]')


@dataclass(frozen=True)
class NotionRootEntity(Generic[RootEntityT]):
    """Base class for Notion-side root entities."""

    notion_id: NotionId
    ref_id: EntityId

    @staticmethod
    def new_notion_entity(entity: RootEntityT) -> 'NotionRootEntity[RootEntityT]':
        """Construct a new Notion row from a given entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    def join_with_entity(self: _NotionRootEntitySubclassT, entity: RootEntityT) -> _NotionRootEntitySubclassT:
        """Add to this Notion row from a given entity."""
        # The subexpression cast is just so we have a reference to Any and pyflakes will shut up!
        return cast(
            _NotionRootEntitySubclassT,
            dataclasses.replace(cast(Any, self.new_notion_entity(entity)), notion_id=self.notion_id))

    def apply_to_entity(self, entity: RootEntityT, modification_time: Timestamp) -> RootEntityT:
        """Obtain the entity form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")


TrunkEntityTypeT = TypeVar('TrunkEntityTypeT', bound=TrunkEntity)
_NotionTrunkEntitySubclassT = TypeVar('_NotionTrunkEntitySubclassT', bound='NotionTrunkEntity[Any]')


@dataclass(frozen=True)
class NotionTrunkEntity(Generic[TrunkEntityTypeT]):
    """Base class for Notion-side trunk entities."""

    notion_id: NotionId
    ref_id: EntityId

    @staticmethod
    def new_notion_entity(entity: TrunkEntityTypeT) -> 'NotionTrunkEntity[TrunkEntityTypeT]':
        """Construct a new Notion row from a given entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    def join_with_entity(self: _NotionTrunkEntitySubclassT, entity: TrunkEntityTypeT) -> _NotionTrunkEntitySubclassT:
        """Add to this Notion row from a given entity."""
        return cast(
            _NotionTrunkEntitySubclassT,
            dataclasses.replace(self.new_notion_entity(entity), notion_id=self.notion_id))


BranchEntityTypeT = TypeVar('BranchEntityTypeT', bound=BranchEntity)
_NotionBranchEntitySubclassT = TypeVar('_NotionBranchEntitySubclassT', bound='NotionBranchEntity[Any]')


@dataclass(frozen=True)
class NotionBranchEntity(Generic[BranchEntityTypeT]):
    """Base class for Notion-side branch entities."""

    notion_id: NotionId
    ref_id: EntityId

    @staticmethod
    def new_notion_entity(entity: BranchEntityTypeT) -> 'NotionBranchEntity[BranchEntityTypeT]':
        """Construct a new Notion row from a given entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    def join_with_entity(self: _NotionBranchEntitySubclassT, entity: BranchEntityTypeT) -> _NotionBranchEntitySubclassT:
        """Add to this Notion row from a given entity."""
        return cast(
            _NotionBranchEntitySubclassT,
            dataclasses.replace(self.new_notion_entity(entity), notion_id=self.notion_id))

    def apply_to_entity(self, entity: BranchEntityTypeT, modification_time: Timestamp) -> BranchEntityTypeT:
        """Obtain the entity form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")


LeafEntityT = TypeVar('LeafEntityT', bound=LeafEntity)
NotionLeafEntityDirectInfoT = TypeVar('NotionLeafEntityDirectInfoT')
NotionLeafEntityInverseInfoT = TypeVar('NotionLeafEntityInverseInfoT')

_NotionLeafEntitySubclassT = TypeVar('_NotionLeafEntitySubclassT', bound='NotionLeafEntity[Any, Any, Any]')


@dataclass(frozen=True)
class NotionLeafApplyToEntityResult(Generic[LeafEntityT]):
    """Result of the apply to entity call."""
    entity: LeafEntityT
    should_modify_on_notion: bool

    @staticmethod
    def just(entity: LeafEntityT) -> 'NotionLeafApplyToEntityResult[LeafEntityT]':
        """Just the entity, but no modification."""
        return NotionLeafApplyToEntityResult(entity, False)


@dataclass(frozen=True)
class NotionLeafEntity(Generic[LeafEntityT, NotionLeafEntityDirectInfoT, NotionLeafEntityInverseInfoT]):
    """Base class for Notion-side leaf entities."""

    notion_id: NotionId
    ref_id: Optional[EntityId]
    archived: bool
    last_edited_time: Timestamp

    @staticmethod
    def new_notion_entity(
            entity: LeafEntityT,
            extra_info: NotionLeafEntityDirectInfoT) \
            -> 'NotionLeafEntity[LeafEntityT, NotionLeafEntityDirectInfoT, NotionLeafEntityInverseInfoT]':
        """Construct a new Notion row from a given entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    def join_with_entity(
            self: _NotionLeafEntitySubclassT,
            entity: LeafEntityT,
            extra_info: NotionLeafEntityDirectInfoT) -> _NotionLeafEntitySubclassT:
        """Add to this Notion row from a given entity."""
        return cast(
            _NotionLeafEntitySubclassT,
            dataclasses.replace(self.new_notion_entity(entity, extra_info), notion_id=self.notion_id))

    def new_entity(self, parent_ref_id: EntityId, extra_info: NotionLeafEntityInverseInfoT) -> LeafEntityT:
        """Construct a new entity from this notion row."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    def apply_to_entity(
            self,
            entity: LeafEntityT,
            extra_info: NotionLeafEntityInverseInfoT) -> NotionLeafApplyToEntityResult[LeafEntityT]:
        """Obtain the entity form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    @property
    def nice_name(self) -> str:
        """A nice name for the Notion-side entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")


BranchTagEntityT = TypeVar('BranchTagEntityT', bound=BranchTagEntity)

_NotionBranchTagEntitySubclassT = TypeVar('_NotionBranchTagEntitySubclassT', bound='NotionBranchTagEntity[Any]')


@dataclass(frozen=True)
class NotionBranchTagEntity(Generic[BranchTagEntityT]):
    """Base class for Notion-side leaf entities."""

    notion_id: NotionId
    ref_id: Optional[EntityId]
    archived: bool
    last_edited_time: Timestamp

    @staticmethod
    def new_notion_entity(entity: BranchTagEntityT) -> 'NotionBranchTagEntity[BranchTagEntityT]':
        """Construct a new Notion row from a given entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    def join_with_entity(
            self: _NotionBranchTagEntitySubclassT, entity: BranchTagEntityT) -> _NotionBranchTagEntitySubclassT:
        """Add to this Notion row from a given entity."""
        return cast(
            _NotionBranchTagEntitySubclassT,
            dataclasses.replace(self.new_notion_entity(entity), notion_id=self.notion_id))

    def new_entity(self, parent_ref_id: EntityId) -> BranchTagEntityT:
        """Construct a new entity from this notion row."""
        raise NotImplementedError("Can't use a base NotionBranchTagEntity class.")

    def apply_to_entity(self, entity: BranchTagEntityT) -> NotionLeafApplyToEntityResult[BranchTagEntityT]:
        """Obtain the entity form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionBranchTagEntity class.")

    @property
    def nice_name(self) -> str:
        """A nice name for the Notion-side entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")
