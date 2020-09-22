"""Some storage utils."""
import abc
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Dict, Any, Protocol, TypeVar, Generic, Optional, List, Tuple, Union, Iterable, FrozenSet

import jsonschema as js
import yaml

from models.basic import EntityId, Timestamp

LOGGER = logging.getLogger(__name__)


class StructuredStorageError(Exception):
    """Exception raised by StructuredIndividualStorage class."""


LiveType = TypeVar("LiveType")

JSONValueType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]  # type: ignore
JSONDictType = Dict[str, JSONValueType]


class StructuredStorageProtocol(Protocol[LiveType]):
    """Protocol for clients of StructuredIndividualStorage to expose."""

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema of the data for this structure storage, as meant for basic storage."""
        ...

    @staticmethod
    def storage_to_live(_storage_form: JSONDictType) -> LiveType:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        ...

    @staticmethod
    def live_to_storage(_live_form: LiveType) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        ...


class StructuredIndividualStorage(Generic[LiveType]):
    """A class for interacting with storage which has a structure (schema, etc.)."""

    _path: Final[Path]
    _protocol: StructuredStorageProtocol[LiveType]

    def __init__(self, path: Path, protocol: StructuredStorageProtocol[LiveType]) -> None:
        """Constructor."""
        self._path = path
        self._protocol = protocol

    def load_optional(self) -> Optional[LiveType]:
        """Load the structured storage fully, but return None if nothing was previously saved."""
        try:
            with self._path.open("r") as store_file:
                data_store = yaml.safe_load(store_file)
                LOGGER.info("Loaded storage")

                js.Draft6Validator(self._protocol.storage_schema()).validate(data_store)
                LOGGER.info("Checked storage structure")

                data_live = self._protocol.storage_to_live(data_store)
                LOGGER.info("Transformed storage to live data")

                return data_live
        except IOError:
            return None
        except (ValueError, yaml.YAMLError, js.ValidationError) as error:
            raise StructuredStorageError from error

    def load(self) -> LiveType:
        """Load the structured storage fully."""
        try:
            with self._path.open("r") as store_file:
                data_store = yaml.safe_load(store_file)
                LOGGER.info("Loaded storage")

                js.Draft6Validator(self._protocol.storage_schema()).validate(data_store)
                LOGGER.info("Checked storage structure")

                data_live = self._protocol.storage_to_live(data_store)
                LOGGER.info("Transformed storage to live data")

                return data_live
        except (IOError, ValueError, yaml.YAMLError, js.ValidationError) as error:
            raise StructuredStorageError from error

    def save(self, data_live: LiveType) -> None:
        """Save the structured storage fully."""
        try:
            with self._path.open("w") as store_file:
                data_store = self._protocol.live_to_storage(data_live)
                LOGGER.info("Transformed live to storage data")

                js.Draft6Validator(self._protocol.storage_schema()).validate(data_store)
                LOGGER.info("Checked new storage structure")

                yaml.dump(data_store, store_file)
                LOGGER.info("Saved storage")
        except (IOError, ValueError, yaml.YAMLError, js.ValidationError) as error:
            raise StructuredStorageError from error


class StructuredCollectionStorage(Generic[LiveType]):
    """A class for interacting with storage for a collection which has a structure (schema, etc.)."""

    _path: Final[Path]
    _protocol: StructuredStorageProtocol[LiveType]
    _live_data: Optional[Tuple[int, List[LiveType]]]

    def __init__(self, path: Path, protocol: StructuredStorageProtocol[LiveType]) -> None:
        """Constructor."""
        self._path = path
        self._protocol = protocol
        self._live_data = None

    def initialize(self) -> None:
        """Initialize."""
        if self._path.exists():
            self._live_data = self._load()
            return
        self._save((0, []))
        self._live_data = (0, [])

    def exit_save(self) -> None:
        """Save before exit."""
        if self._live_data is None:
            raise Exception("Called exit_save without a prior call to initialize!")
        self._save(self._live_data)

    def insert(self, live: LiveType, set_ref_id: bool = False) -> None:
        """Add a new element to the collection."""
        storage_idx, storage = self.load()
        storage.append(live)
        if set_ref_id:
            setattr(live, "ref_id", str(storage_idx))
        self.save((storage_idx + 1, storage))

    def update(self, live: LiveType, **kwargs: Any) -> None:  # type: ignore
        """Update an existing element identified by the filtering expression."""
        storage_idx, storage = self.load()

        for elem_idx, elem in enumerate(storage):
            for filter_key, filter_value in kwargs.items():
                try:
                    elem_value = getattr(elem, filter_key)
                    if elem_value != filter_value:
                        break
                except AttributeError:
                    break
            else:
                storage[elem_idx] = live
                self.save((storage_idx, storage))
                return

        filter_expr_str = " ".join(f"{k}={v}" for (k, v) in kwargs.items())
        raise StructuredStorageError(f"Element identified by '{filter_expr_str}' does not exist")

    def remove(self, **kwargs: Any) -> LiveType:  # type: ignore
        """Remove the item identified by the filtering expression."""
        storage_idx, storage = self.load()

        for elem_idx, elem in enumerate(storage):
            for filter_key, filter_value in kwargs.items():
                try:
                    elem_value = getattr(elem, filter_key)
                    if elem_value != filter_value:
                        break
                except AttributeError:
                    break
            else:
                found_elem = storage[elem_idx]
                del storage[elem_idx]
                self.save((storage_idx, storage))
                return found_elem

        filter_expr_str = " ".join(f"{k}={v}" for (k, v) in kwargs.items())
        raise StructuredStorageError(f"Element identified by '{filter_expr_str}' does not exist")

    def remove_all(self, **kwargs: Any) -> None:  # type: ignore
        """Remove the item identified by the filtering expression."""
        storage_idx, storage = self.load()

        def _build_new() -> Iterable[LiveType]:
            for _, elem in enumerate(storage):
                for filter_key, filter_value in kwargs.items():
                    try:
                        elem_value = getattr(elem, filter_key)
                        if elem_value != filter_value:
                            yield elem
                            break
                    except AttributeError:
                        yield elem
                        break

        new_storage = list(_build_new())
        self.save((storage_idx, new_storage))

    def find_by_property(self, **kwargs: Any) -> Optional[LiveType]:  # type: ignore
        """Find the first element in the collection matching all the properties."""
        _, storage = self.load()
        for elem in storage:
            for filter_key, filter_value in kwargs.items():
                try:
                    elem_value = getattr(elem, filter_key)
                    if elem_value != filter_value:
                        break
                except AttributeError:
                    break
            else:
                return elem

        return None

    def find_by_property_strict(self, **kwargs: Any) -> LiveType:  # type: ignore
        """Find the first element in the collection matching all the properties."""
        _, storage = self.load()
        for elem in storage:
            for filter_key, filter_value in kwargs.items():
                try:
                    elem_value = getattr(elem, filter_key)
                    if elem_value != filter_value:
                        break
                except AttributeError:
                    break
            else:
                return elem

        filter_expr_str = " ".join(f"{k}={v}" for (k, v) in kwargs.items())
        raise StructuredStorageError(f"Element identified by '{filter_expr_str}' does not exist")

    def find_all_by_property(self, **kwargs: Any) -> Iterable[LiveType]:  # type: ignore
        """Find all the elements in the collection matching all the properties."""
        _, storage = self.load()
        for elem in storage:
            for filter_key, filter_value in kwargs.items():
                try:
                    elem_value = getattr(elem, filter_key)
                    if elem_value != filter_value:
                        break
                except AttributeError:
                    break
            else:
                yield elem

    def load(self) -> Tuple[int, List[LiveType]]:
        """Load the structured storage fully."""
        if self._live_data is None:
            raise Exception("Called exit_save without a prior call to initialize!")
        return self._live_data

    def save(self, new_storage: Tuple[int, List[LiveType]]) -> None:
        """Save the structured storage fully."""
        self._live_data = new_storage
        self._save(self._live_data)

    def _load(self) -> Tuple[int, List[LiveType]]:
        try:
            with self._path.open("r") as store_file:
                data_store = yaml.safe_load(store_file)
                LOGGER.info("Loaded storage")

                js.Draft6Validator(self._get_full_schema()).validate(data_store)
                LOGGER.info("Checked storage structure")

                next_idx = data_store["next_idx"]
                entries = [self._protocol.storage_to_live(entry) for entry in data_store["entries"]]
                LOGGER.info("Transformed storage to live data")

                return next_idx, entries
        except (IOError, ValueError, yaml.YAMLError, js.ValidationError) as error:
            raise StructuredStorageError from error

    def _save(self, new_storage: Tuple[int, List[LiveType]]) -> None:
        try:
            with self._path.open("w") as store_file:
                data_store = {
                    "next_idx": new_storage[0],
                    "entries": [self._protocol.live_to_storage(entry) for entry in new_storage[1]]
                }
                LOGGER.info("Transformed live to storage data")

                js.Draft6Validator(self._get_full_schema()).validate(data_store)
                LOGGER.info("Checked new storage structure")

                yaml.dump(data_store, store_file)
                LOGGER.info("Saved storage")
        except (IOError, ValueError, yaml.YAMLError, js.ValidationError) as error:
            raise StructuredStorageError from error

    def _get_full_schema(self) -> JSONDictType:
        return {
            "type": "object",
            "properties": {
                "next_idx": {"type": "number"},
                "entries": {
                    "type": "array",
                    "items": self._protocol.storage_schema()
                }
            }
        }


@dataclass()
class BaseEntity:
    """The base class for all entities."""

    ref_id: EntityId
    archived: bool
    created_time: Timestamp
    last_modified_time: Timestamp
    archived_time: Optional[Timestamp]


EntityType = TypeVar("EntityType", bound=BaseEntity)

FindFilterType = Union[None, bool, int, float, str]


class FindFilterPredicate(abc.ABC):
    """A predicate for the find function."""

    @abc.abstractmethod
    def test(self, val: FindFilterType) -> bool:
        """Test whether the predicate is matched against a value."""


class Eq(FindFilterPredicate):
    """A filtering predicate for exact equality."""

    _filter_val: Final[FindFilterType]

    def __init__(self, filter_val: FindFilterType) -> None:
        """Constructor."""
        self._filter_val = filter_val

    def test(self, val: FindFilterType) -> bool:
        """Test whether the predicate is matched against a value."""
        return self._filter_val == val


class In:
    """A filtering predicate for membership in a set."""

    _filter_set: Final[FrozenSet[FindFilterType]]

    def __init__(self, *filter_set: FindFilterType) -> None:
        """Constructor."""
        self._filter_set = frozenset(filter_set)

    def test(self, val: FindFilterType) -> bool:
        """Test whether the predicate is matched against a value."""
        return val in self._filter_set


class EntityCollectionStorage(Generic[EntityType]):
    """A class for interacting with storage for a collection of entities which has a structure (schema, etc.)."""

    _path: Final[Path]
    _protocol: StructuredStorageProtocol[EntityType]

    def __init__(self, path: Path, protocol: StructuredStorageProtocol[EntityType]) -> None:
        """Constructor."""
        self._path = path
        self._protocol = protocol

    def initialize(self) -> None:
        """Initialize."""
        if self._path.exists():
            return
        self._save(0, [])

    def insert(self, entity: EntityType) -> EntityType:
        """Add a new entity to the storage and assign an id for it."""
        next_idx, entities = self._load()
        entity.ref_id = EntityId(str(next_idx))
        entities.append(entity)
        self._save(next_idx + 1, entities)
        return entity

    def update(self, new_entity: EntityType) -> EntityType:
        """Update an existing element."""
        next_idx, entities = self._load()

        for entity_idx, entity in enumerate(entities):
            if entity.ref_id == new_entity.ref_id:
                entities[entity_idx] = new_entity
                self._save(next_idx, entities)
                return new_entity

        raise StructuredStorageError(f"Element identified by {new_entity.ref_id} does not exist")

    def remove(self, ref_id: EntityId) -> EntityType:
        """Remove the item identified by the ref id."""
        next_idx, entities = self._load()

        for entity_idx, entity in enumerate(entities):
            if entity.ref_id == ref_id:
                del entities[entity_idx]
                self._save(next_idx, entities)
                return entity

        raise StructuredStorageError(f"Element identified by {ref_id} does not exist")

    def load(self, ref_id: EntityId, allow_archived: bool = False) -> EntityType:
        """Retrieve the item identified by the ref id."""
        _, entities = self._load()

        for entity_idx, entity in enumerate(entities):
            if entity.ref_id != ref_id:
                continue

            if not allow_archived and entity.archived:
                raise StructuredStorageError(f"Element identified by {ref_id} is archived")

            return entity

        raise StructuredStorageError(f"Element identified by {ref_id} does not exist")

    def load_optional(self, ref_id: EntityId, allow_archived: bool = False) -> Optional[EntityType]:
        """Retrieve the item identified by the ref id."""
        _, entities = self._load()

        for entity_idx, entity in enumerate(entities):
            if entity.ref_id != ref_id:
                continue

            if not allow_archived and entity.archived:
                raise StructuredStorageError(f"Element identified by {ref_id} is archived")

            return entity

        return None

    def find_all(self, **kwargs: FindFilterPredicate) -> Iterable[EntityType]:
        """Find all the elements in the collection matching all the properties."""
        _, entities = self._load()

        for entity in entities:
            for filter_property_name, filter_predicate in kwargs.items():
                try:
                    property_value = getattr(entity, filter_property_name)
                    if not filter_predicate.test(property_value):
                        break
                except AttributeError:
                    raise StructuredStorageError(
                        f"Element identified by {entity.ref_id} does not have property {filter_property_name}")
            else:
                yield entity

    def _load(self) -> Tuple[int, List[EntityType]]:
        try:
            with self._path.open("r") as store_file:
                data_store = yaml.safe_load(store_file)
                LOGGER.info("Loaded storage")

                js.Draft6Validator(self._get_full_schema()).validate(data_store)
                LOGGER.info("Checked storage structure")

                next_idx = data_store["next_idx"]
                entities = [self._protocol.storage_to_live(entry) for entry in data_store["entities"]]
                LOGGER.info("Transformed storage to live data")

                return next_idx, entities
        except (IOError, ValueError, yaml.YAMLError, js.ValidationError) as error:
            raise StructuredStorageError from error

    def _save(self, new_next_idx: int, new_entities: List[EntityType]) -> None:
        try:
            with self._path.open("w") as store_file:
                data_store = {
                    "next_idx": new_next_idx,
                    "entities": [self._protocol.live_to_storage(entry) for entry in new_entities]
                }
                LOGGER.info("Transformed live to storage data")

                js.Draft6Validator(self._get_full_schema()).validate(data_store)
                LOGGER.info("Checked new storage structure")

                yaml.dump(data_store, store_file)
                LOGGER.info("Saved storage")
        except (IOError, ValueError, yaml.YAMLError, js.ValidationError) as error:
            raise StructuredStorageError from error

    def _get_full_schema(self) -> JSONDictType:
        return {
            "type": "object",
            "properties": {
                "next_idx": {"type": "number"},
                "entities": {
                    "type": "array",
                    "items": self._protocol.storage_schema()
                }
            }
        }
