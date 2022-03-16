"""Framework level elements for the Notion concepts."""
import dataclasses
from dataclasses import dataclass
from typing import Any, Optional, Generic, TypeVar, cast

from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.entity import LeafEntity, TrunkEntity, BranchEntity, RootEntity, BranchTagEntity

RootEntityType = TypeVar('RootEntityType', bound=RootEntity)
_NotionRootEntitySubclass = TypeVar('_NotionRootEntitySubclass', bound='NotionRootEntity[Any]')


@dataclass(frozen=True)
class NotionRootEntity(Generic[RootEntityType]):
    """Base class for Notion-side root entities."""

    notion_id: NotionId
    ref_id: EntityId

    @staticmethod
    def new_notion_entity(entity: RootEntityType) -> 'NotionRootEntity[RootEntityType]':
        """Construct a new Notion row from a given entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    def join_with_entity(self: _NotionRootEntitySubclass, entity: RootEntityType) -> _NotionRootEntitySubclass:
        """Add to this Notion row from a given entity."""
        # The subexpression cast is just so we have a reference to Any and pyflakes will shut up!
        return cast(
            _NotionRootEntitySubclass,
            dataclasses.replace(cast(Any, self.new_notion_entity(entity)), notion_id=self.notion_id))

    def apply_to_entity(self, entity: RootEntityType, modification_time: Timestamp) -> RootEntityType:
        """Obtain the entity form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")


TrunkEntityType = TypeVar('TrunkEntityType', bound=TrunkEntity)
_NotionTrunkEntitySubclass = TypeVar('_NotionTrunkEntitySubclass', bound='NotionTrunkEntity[Any]')


@dataclass(frozen=True)
class NotionTrunkEntity(Generic[TrunkEntityType]):
    """Base class for Notion-side trunk entities."""

    notion_id: NotionId
    ref_id: EntityId

    @staticmethod
    def new_notion_entity(entity: TrunkEntityType) -> 'NotionTrunkEntity[TrunkEntityType]':
        """Construct a new Notion row from a given entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    def join_with_entity(self: _NotionTrunkEntitySubclass, entity: TrunkEntityType) -> _NotionTrunkEntitySubclass:
        """Add to this Notion row from a given entity."""
        return cast(
            _NotionTrunkEntitySubclass,
            dataclasses.replace(self.new_notion_entity(entity), notion_id=self.notion_id))


BranchEntityType = TypeVar('BranchEntityType', bound=BranchEntity)
_NotionBranchEntitySubclass = TypeVar('_NotionBranchEntitySubclass', bound='NotionBranchEntity[Any]')


@dataclass(frozen=True)
class NotionBranchEntity(Generic[BranchEntityType]):
    """Base class for Notion-side branch entities."""

    notion_id: NotionId
    ref_id: EntityId

    @staticmethod
    def new_notion_entity(entity: BranchEntityType) -> 'NotionBranchEntity[BranchEntityType]':
        """Construct a new Notion row from a given entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    def join_with_entity(self: _NotionBranchEntitySubclass, entity: BranchEntityType) -> _NotionBranchEntitySubclass:
        """Add to this Notion row from a given entity."""
        return cast(
            _NotionBranchEntitySubclass,
            dataclasses.replace(self.new_notion_entity(entity), notion_id=self.notion_id))

    def apply_to_entity(self, entity: BranchEntityType, modification_time: Timestamp) -> BranchEntityType:
        """Obtain the entity form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")


LeafEntityType = TypeVar('LeafEntityType', bound=LeafEntity)
NotionLeafEntityDirectInfoType = TypeVar('NotionLeafEntityDirectInfoType')
NotionLeafEntityInverseInfoType = TypeVar('NotionLeafEntityInverseInfoType')

_NotionLeafEntitySubclass = TypeVar('_NotionLeafEntitySubclass', bound='NotionLeafEntity[Any, Any, Any]')


@dataclass(frozen=True)
class NotionLeafApplyToEntityResult(Generic[LeafEntityType]):
    """Result of the apply to entity call."""
    entity: LeafEntityType
    should_modify_on_notion: bool

    @staticmethod
    def just(entity: LeafEntityType) -> 'NotionLeafApplyToEntityResult[LeafEntityType]':
        """Just the entity, but no modification."""
        return NotionLeafApplyToEntityResult(entity, False)


@dataclass(frozen=True)
class NotionLeafEntity(Generic[LeafEntityType, NotionLeafEntityDirectInfoType, NotionLeafEntityInverseInfoType]):
    """Base class for Notion-side leaf entities."""

    notion_id: NotionId
    ref_id: Optional[EntityId]
    archived: bool
    last_edited_time: Timestamp

    @staticmethod
    def new_notion_entity(
            entity: LeafEntityType,
            extra_info: NotionLeafEntityDirectInfoType) \
            -> 'NotionLeafEntity[LeafEntityType, NotionLeafEntityDirectInfoType, NotionLeafEntityInverseInfoType]':
        """Construct a new Notion row from a given entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    def join_with_entity(
            self: _NotionLeafEntitySubclass,
            entity: LeafEntityType,
            extra_info: NotionLeafEntityDirectInfoType) -> _NotionLeafEntitySubclass:
        """Add to this Notion row from a given entity."""
        return cast(
            _NotionLeafEntitySubclass,
            dataclasses.replace(self.new_notion_entity(entity, extra_info), notion_id=self.notion_id))

    def new_entity(self, parent_ref_id: EntityId, extra_info: NotionLeafEntityInverseInfoType) -> LeafEntityType:
        """Construct a new entity from this notion row."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    def apply_to_entity(
            self,
            entity: LeafEntityType,
            extra_info: NotionLeafEntityInverseInfoType) -> NotionLeafApplyToEntityResult[LeafEntityType]:
        """Obtain the entity form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    @property
    def nice_name(self) -> str:
        """A nice name for the Notion-side entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")


BranchTagEntityType = TypeVar('BranchTagEntityType', bound=BranchTagEntity)

_NotionBranchTagEntitySubclass = TypeVar('_NotionBranchTagEntitySubclass', bound='NotionBranchTagEntity[Any]')


@dataclass(frozen=True)
class NotionBranchTagEntity(Generic[BranchTagEntityType]):
    """Base class for Notion-side leaf entities."""

    notion_id: NotionId
    ref_id: Optional[EntityId]
    archived: bool
    last_edited_time: Timestamp

    @staticmethod
    def new_notion_entity(entity: BranchTagEntityType) -> 'NotionBranchTagEntity[BranchTagEntityType]':
        """Construct a new Notion row from a given entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")

    def join_with_entity(
            self: _NotionBranchTagEntitySubclass, entity: BranchTagEntityType) -> _NotionBranchTagEntitySubclass:
        """Add to this Notion row from a given entity."""
        return cast(
            _NotionBranchTagEntitySubclass,
            dataclasses.replace(self.new_notion_entity(entity), notion_id=self.notion_id))

    def new_entity(self, parent_ref_id: EntityId) -> BranchTagEntityType:
        """Construct a new entity from this notion row."""
        raise NotImplementedError("Can't use a base NotionBranchTagEntity class.")

    def apply_to_entity(self, entity: BranchTagEntityType) -> NotionLeafApplyToEntityResult[BranchTagEntityType]:
        """Obtain the entity form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionBranchTagEntity class.")

    @property
    def nice_name(self) -> str:
        """A nice name for the Notion-side entity."""
        raise NotImplementedError("Can't use a base NotionLeafEntity class.")
