"""Some storage utils."""
import abc
import collections
import hashlib
import logging
import typing
from dataclasses import dataclass, field
from enum import Enum
from itertools import chain
from pathlib import Path
from typing import Final, Dict, Protocol, TypeVar, Generic, Optional, List, Tuple, Union, Iterable, FrozenSet

import jsonschema as js
import pendulum
import yaml

from framework.base.entity_id import EntityId
from framework.base.timestamp import Timestamp
from framework.json import JSONDictType
from framework.value import Value
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class StorageEntityNotFoundError(Exception):
    """Exception raised when a particular entity is not found."""


LiveType = TypeVar("LiveType")

FindFilterType = Union[None, bool, int, float, str, List[int], Enum, Value]


class FindFilterPredicate(abc.ABC):
    """A predicate for the find function."""

    @abc.abstractmethod
    def test(self, val: FindFilterType) -> bool:
        """Test whether the predicate is matched against a value."""

    @abc.abstractmethod
    def as_operator_str(self, val: FindFilterType) -> str:
        """Represent what this predicate is doing."""


class Eq(FindFilterPredicate):
    """A filtering predicate for exact equality."""

    _filter_val: Final[FindFilterType]

    def __init__(self, filter_val: FindFilterType) -> None:
        """Constructor."""
        self._filter_val = filter_val

    def test(self, val: FindFilterType) -> bool:
        """Test whether the predicate is matched against a value."""
        return self._filter_val == val

    def as_operator_str(self, val: FindFilterType) -> str:
        """Represent what this predicate is doing."""
        return f"{val} == {self._filter_val}"


class In(FindFilterPredicate):
    """A filtering predicate for membership in a set."""

    _filter_set: Final[FrozenSet[FindFilterType]]

    def __init__(self, *filter_set: FindFilterType) -> None:
        """Constructor."""
        self._filter_set = frozenset(filter_set)

    def test(self, val: FindFilterType) -> bool:
        """Test whether the predicate is matched against a value."""
        return val in self._filter_set

    def as_operator_str(self, val: FindFilterType) -> str:
        """Represent what this predicate is doing."""
        return f"{val} in ({','.join(str(s) for s in self._filter_set)})"


class Intersect(FindFilterPredicate):
    """A filtering predicate for intersection with a set."""

    _filter_set: Final[FrozenSet[FindFilterType]]

    def __init__(self, *filter_set: FindFilterType) -> None:
        """Constructor."""
        self._filter_set = frozenset(filter_set)

    def test(self, val: FindFilterType) -> bool:
        """Test whether the predicate is matched against a value."""
        if isinstance(val, collections.Iterable):
            return len(self._filter_set.intersection(val)) > 0
        else:
            return val in self._filter_set

    def as_operator_str(self, val: FindFilterType) -> str:
        """Represent what this predicate is doing."""
        if isinstance(val, list):
            return f"({','.join(str(u) for u in val)}) intersect ({','.join(str(s) for s in self._filter_set)})"
        else:
            return f"({val}) intersect ({','.join(str(s) for s in self._filter_set)})"


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

    def save(self, data_live: LiveType) -> None:
        """Create the structured storage fully."""
        with self._path.open("w") as store_file:
            data_store = self._protocol.live_to_storage(data_live)
            LOGGER.info("Transformed live to storage data")

            js.Draft6Validator(self._protocol.storage_schema()).validate(data_store)
            LOGGER.info("Checked new storage structure")

            yaml.dump(data_store, store_file)
            LOGGER.info("Saved storage")

    def load_optional(self) -> Optional[LiveType]:
        """Load the structured storage fully, but return None if nothing was previously saved."""
        try:
            with self._path.open("r") as store_file:
                data_store = yaml.safe_load(store_file)
                LOGGER.info("Loaded storage")
        except IOError:
            return None

        js.Draft6Validator(self._protocol.storage_schema()).validate(data_store)
        LOGGER.info("Checked storage structure")

        data_live = self._protocol.storage_to_live(data_store)
        LOGGER.info("Transformed storage to live data")

        return data_live

    def load(self) -> LiveType:
        """Load the structured storage fully."""
        try:
            with self._path.open("r") as store_file:
                data_store = yaml.safe_load(store_file)
                LOGGER.info("Loaded storage")
        except IOError as err:
            raise StorageEntityNotFoundError from err

        js.Draft6Validator(self._protocol.storage_schema()).validate(data_store)
        LOGGER.info("Checked storage structure")

        data_live = self._protocol.storage_to_live(data_store)
        LOGGER.info("Transformed storage to live data")

        return data_live


BAD_REF_ID = EntityId("bad-entity-id")
BAD_TIME = Timestamp(pendulum.datetime(2000, 1, 1))


@dataclass()
class BaseRecordRow:
    """The base class for all records."""
    key: str
    created_time: Timestamp = field(init=False)
    last_modified_time: Timestamp = field(init=False)

    def __post_init__(self) -> None:
        """Init the base record with some invalid data."""
        self.created_time = BAD_TIME
        self.last_modified_time = BAD_TIME


RecordRowType = TypeVar("RecordRowType", bound=BaseRecordRow)


class RecordsStorage(Generic[RecordRowType]):
    """A class for interacting with storage for a collection of records which has a structure (schema, etc.)."""

    BASE_RECORD_ROW_PROPERTIES = {
        "key": {"type": "string"},
        "created_time": {"type": "string"},
        "last_modified_time": {"type": "string"}
    }

    _path: Final[Path]
    _time_provider: Final[TimeProvider]
    _protocol: StructuredStorageProtocol[RecordRowType]
    _full_entity_schema: Final[JSONDictType]

    def __init__(
            self, path: Path, time_provider: TimeProvider, protocol: StructuredStorageProtocol[RecordRowType]) -> None:
        """Constructor."""
        self._path = path
        self._time_provider = time_provider
        self._protocol = protocol

        items_schema: JSONDictType = {}
        for key0, val0 in self.BASE_RECORD_ROW_PROPERTIES.items():
            items_schema[key0] = val0
        for key1, val1 in self._protocol.storage_schema().items():
            items_schema[key1] = val1
        self._full_entity_schema = {
            "type": "object",
            "properties": {
                "next_idx": {"type": "number"},
                "records": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": items_schema
                    }
                }
            }
        }

    def initialize(self) -> None:
        """Initialize."""
        if self._path.exists():
            return
        self._save(0, [])

    def create(self, record: RecordRowType) -> RecordRowType:
        """Add a new record to the storage."""
        next_idx, records = self._load()

        record.created_time = self._time_provider.get_current_time()
        record.last_modified_time = self._time_provider.get_current_time()

        records.append(record)
        self._save(next_idx + 1, records)

        return record

    def remove(self, key: str) -> RecordRowType:
        """Remove the record identified by the key."""
        next_idx, records = self._load()

        for record_idx, record in enumerate(records):
            if record.key == key:
                del records[record_idx]
                self._save(next_idx, records)
                return record

        raise StorageEntityNotFoundError(f"Record identified by {key} does not exist")

    def update(self, new_record: RecordRowType) -> RecordRowType:
        """Update an existing record."""
        next_idx, records = self._load()

        for record_idx, record in enumerate(records):
            if record.key == new_record.key:
                new_record.last_modified_time = self._time_provider.get_current_time()
                records[record_idx] = new_record
                self._save(next_idx, records)
                return new_record

        raise StorageEntityNotFoundError(f"Record identified by {new_record.key} does not exist")

    def load(self, key: str) -> RecordRowType:
        """Retrieve the record identified by the key."""
        _, records = self._load()

        for record in records:
            if record.key != key:
                continue

            return record

        raise StorageEntityNotFoundError(f"Record identified by {key} does not exist")

    def load_optional(self, key: str) -> Optional[RecordRowType]:
        """Retrieve the record identified by the ref id."""
        _, records = self._load()

        for record in records:
            if record.key != key:
                continue

            return record

        return None

    def find_all(self, **kwargs: Optional[FindFilterPredicate]) -> List[RecordRowType]:
        """Find all the records in the collection matching all the properties."""
        _, records = self._load()

        def _find_all() -> Iterable[RecordRowType]:
            for record in records:
                for filter_property_name, filter_predicate in kwargs.items():
                    if filter_predicate is None:
                        continue

                    try:
                        property_value = getattr(record, filter_property_name)
                        if not filter_predicate.test(property_value):
                            break
                    except AttributeError:
                        raise Exception(
                            f"Record identified by {record.key} does not have property {filter_property_name}")
                else:
                    yield record

        return list(_find_all())

    def _load(self) -> Tuple[int, List[RecordRowType]]:
        with self._path.open("r") as store_file:
            data_store = yaml.safe_load(store_file)
            LOGGER.info("Loaded storage")

            js.Draft6Validator(self._full_entity_schema).validate(data_store)
            LOGGER.info("Checked storage structure")

            next_idx = data_store["next_idx"]
            records = [self._full_storage_form_to_record(record) for record in data_store["records"]]
            LOGGER.info("Transformed storage to live data")

            return next_idx, records

    def _save(self, new_next_idx: int, new_records: List[RecordRowType]) -> None:
        with self._path.open("w") as store_file:
            data_store = {
                "next_idx": new_next_idx,
                "records": [self._entity_to_full_storage_form(entity) for entity in new_records]
            }
            LOGGER.info("Transformed live to storage data")

            js.Draft6Validator(self._full_entity_schema).validate(data_store)
            LOGGER.info("Checked new storage structure")

            yaml.dump(data_store, store_file)
            LOGGER.info("Saved storage")

    def _full_storage_form_to_record(self, full_storage_form: JSONDictType) -> RecordRowType:
        record = self._protocol.storage_to_live(full_storage_form)
        record.created_time = Timestamp.from_str(typing.cast(str, full_storage_form["created_time"]))
        record.last_modified_time = Timestamp.from_str(typing.cast(str, full_storage_form["last_modified_time"]))
        return record

    def _entity_to_full_storage_form(self, record: RecordRowType) -> JSONDictType:
        full_storage_form: JSONDictType = {
            "key": record.key,
            "created_time": str(record.created_time),
            "last_modified_time": str(record.last_modified_time)
        }
        for key, val in self._protocol.live_to_storage(record).items():
            full_storage_form[key] = val
        return full_storage_form


@dataclass()
class BaseEntityRow:
    """The base class for all entities."""

    ref_id: EntityId = field(init=False)
    archived: bool
    created_time: Timestamp = field(init=False)
    last_modified_time: Timestamp = field(init=False)
    archived_time: Optional[Timestamp] = field(init=False)

    def __post_init__(self) -> None:
        """Init the base entity with some invalid data."""
        self.ref_id = BAD_REF_ID
        self.created_time = BAD_TIME
        self.last_modified_time = BAD_TIME
        self.archived_time = None


EntityRowType = TypeVar("EntityRowType", bound=BaseEntityRow)


class EntitiesStorage(Generic[EntityRowType]):
    """A class for interacting with storage for a collection of entities which has a structure (schema, etc.)."""

    _BASE_ENTITY_ROW_PROPERTIES = {
        "ref_id": {"type": "string"},
        "archived": {"type": "boolean"},
        "created_time": {"type": "string"},
        "last_modified_time": {"type": "string"},
        "archived_time": {"type": ["string", "null"]}
    }

    _METADATA_SCHEMA = {
        "type": "object",
        "properties": {
            "next_idx": {"type": "number"}
        }
    }

    _path: Final[Path]
    _num_shards: Final[int]
    _time_provider: Final[TimeProvider]
    _protocol: StructuredStorageProtocol[EntityRowType]
    _full_entity_schema: Final[JSONDictType]

    def __init__(
            self, path: Path, num_shards: int, time_provider: TimeProvider,
            protocol: StructuredStorageProtocol[EntityRowType]) -> None:
        """Constructor."""
        self._path = path
        self._num_shards = num_shards
        self._time_provider = time_provider
        self._protocol = protocol

        items_schema = {}
        for key0, val0 in self._BASE_ENTITY_ROW_PROPERTIES.items():
            items_schema[key0] = val0
        for key1, val1 in self._protocol.storage_schema().items():
            items_schema[key1] = val1
        self._full_entity_schema = {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": items_schema
                    }
                }
            }
        }

    def initialize(self) -> None:
        """Initialize."""
        if self._path.exists():
            return
        for shard_id in self._get_all_shard_ids():
            self._save(shard_id, 0, [])

    def create(self, entity: EntityRowType) -> EntityRowType:
        """Add a new entity to the storage and assign an id for it."""
        if entity.ref_id != BAD_REF_ID:
            raise Exception(f"Cannot insert entity with preassigned id {entity.ref_id}")

        next_idx = self._load_metadata()

        entity.ref_id = EntityId(str(next_idx))
        entity.created_time = self._time_provider.get_current_time()
        entity.last_modified_time = self._time_provider.get_current_time()
        entity.archived_time = self._time_provider.get_current_time() if entity.archived else None

        shard_id = self._get_shard_id(entity.ref_id)
        _, entities = self._load(shard_id)

        entities.append(entity)
        # Oopsie - next_idx might have changed!
        self._save(shard_id, next_idx + 1, entities)

        return entity

    def remove(self, ref_id: EntityId) -> EntityRowType:
        """Remove the entity identified by the ref id."""
        if ref_id == BAD_REF_ID:
            raise Exception(f"Cannot remove entity without a good id")

        shard_id = self._get_shard_id(ref_id)

        next_idx, entities = self._load(shard_id)

        for entity_idx, entity in enumerate(entities):
            if entity.ref_id == ref_id:
                del entities[entity_idx]
                self._save(shard_id, next_idx, entities)
                return entity

        raise StorageEntityNotFoundError(f"Entity identified by {ref_id} does not exist")

    def update(self, new_entity: EntityRowType) -> EntityRowType:
        """Update an existing entity."""
        if new_entity.ref_id == BAD_REF_ID:
            raise Exception(f"Cannot update entity without a good id")

        shard_id = self._get_shard_id(new_entity.ref_id)

        next_idx, entities = self._load(shard_id)

        for entity_idx, entity in enumerate(entities):
            if entity.ref_id == new_entity.ref_id:
                new_entity.last_modified_time = self._time_provider.get_current_time()
                entities[entity_idx] = new_entity
                self._save(shard_id, next_idx, entities)
                return new_entity

        raise StorageEntityNotFoundError(f"Entity identified by {new_entity.ref_id} does not exist")

    def dump_all(self, entities: Iterable[EntityRowType]) -> None:
        """Dump and overwrite all entities."""
        all_datas: Dict[int, List[EntityRowType]] = {shard_id: [] for shard_id in self._get_all_shard_ids()}

        next_idx, _ = self._load(0)

        for entity in entities:
            all_datas[self._get_shard_id(entity.ref_id)].append(entity)

        for shard_id, shard_data in all_datas.items():
            self._save(shard_id, next_idx, shard_data)

    def load(self, ref_id: EntityId, allow_archived: bool = False) -> EntityRowType:
        """Retrieve the entity identified by the ref id."""
        if ref_id == BAD_REF_ID:
            raise Exception(f"Cannot remove entity without a good id")

        shard_id = self._get_shard_id(ref_id)

        _, entities = self._load(shard_id)

        for entity in entities:
            if entity.ref_id != ref_id:
                continue

            if not allow_archived and entity.archived:
                raise StorageEntityNotFoundError(f"Entity identified by {ref_id} is archived")

            return entity

        raise StorageEntityNotFoundError(f"Entity identified by {ref_id} does not exist")

    def load_optional(self, ref_id: EntityId, allow_archived: bool = False) -> Optional[EntityRowType]:
        """Retrieve the entity identified by the ref id."""
        if ref_id == BAD_REF_ID:
            raise Exception(f"Cannot remove entity without a good id")

        shard_id = self._get_shard_id(ref_id)

        _, entities = self._load(shard_id)

        for entity in entities:
            if entity.ref_id != ref_id:
                continue

            if not allow_archived and entity.archived:
                raise StorageEntityNotFoundError(f"Entity identified by {ref_id} is archived")

            return entity

        return None

    def find_first(
            self, allow_archived: bool = False, **kwargs: Optional[FindFilterPredicate]) -> EntityRowType:
        """Find all the entities in the collection matching all the properties."""
        for shard_id in self._get_all_shard_ids():
            _, entities = self._load(shard_id)

            for entity in entities:
                for filter_property_name, filter_predicate in kwargs.items():
                    if filter_predicate is None:
                        continue

                    try:
                        property_value = getattr(entity, filter_property_name)
                        if not filter_predicate.test(property_value):
                            break
                    except AttributeError:
                        raise Exception(
                            f"Entity identified by {entity.ref_id} does not have property {filter_property_name}")
                else:
                    if not allow_archived and entity.archived:
                        continue

                    return entity

        filter_expr = " & ".join(f"{v.as_operator_str(k)}" for k, v in kwargs.items() if v is not None)
        raise StorageEntityNotFoundError(f"Entity identified by {filter_expr} is archived")

    def find_all(
            self, allow_archived: bool = False, **kwargs: Optional[FindFilterPredicate]) -> List[EntityRowType]:
        """Find all the entities in the collection matching all the properties."""
        def _find_all(shard_id: int) -> Iterable[EntityRowType]:
            _, entities = self._load(shard_id)

            for entity in entities:
                for filter_property_name, filter_predicate in kwargs.items():
                    if filter_predicate is None:
                        continue

                    try:
                        property_value = getattr(entity, filter_property_name)
                        if not filter_predicate.test(property_value):
                            break
                    except AttributeError:
                        raise Exception(
                            f"Entity identified by {entity.ref_id} does not have property {filter_property_name}")
                else:
                    if not allow_archived and entity.archived:
                        continue

                    yield entity

        return list(chain.from_iterable(_find_all(shard_id) for shard_id in self._get_all_shard_ids()))

    def _load_metadata(self) -> int:
        with self._get_metadata_path().open("r") as metadata_file:
            metadata_store = yaml.safe_load(metadata_file)
            LOGGER.info("Loaded metadata")

            js.Draft6Validator(self._METADATA_SCHEMA).validate(metadata_store)
            LOGGER.info("Checked metadata")

            next_idx = typing.cast(int, metadata_store["next_idx"])

            return next_idx

    def _load(self, shard_id: int) -> Tuple[int, List[EntityRowType]]:
        with self._get_metadata_path().open("r") as metadata_file:
            metadata_store = yaml.safe_load(metadata_file)
            LOGGER.info("Loaded metadata")

            js.Draft6Validator(self._METADATA_SCHEMA).validate(metadata_store)
            LOGGER.info("Checked metadata")

            next_idx = metadata_store["next_idx"]

        with self._get_shard_path(shard_id).open("r") as shard_file:
            shard_store = yaml.safe_load(shard_file)
            LOGGER.info("Loaded shard")

            js.Draft6Validator(self._full_entity_schema).validate(shard_store)
            LOGGER.info("Checked shard")
            entities = [self._full_storage_form_to_entity(entity) for entity in shard_store["entities"]]
            LOGGER.info("Transformed storage to live data")

        return next_idx, entities

    def _save(self, shard_id: int, new_next_idx: int, new_entities: List[EntityRowType]) -> None:
        self._path.mkdir(exist_ok=True)

        with self._get_metadata_path().open("w") as metadata_file:
            metadata = {
                "next_idx": new_next_idx
            }
            yaml.dump(metadata, metadata_file)
            LOGGER.info("Saved metadata")

        with self._get_shard_path(shard_id).open("w") as shard_file:
            data_store = {
                "entities": [self._entity_to_full_storage_form(entity) for entity in new_entities]
            }
            LOGGER.info("Transformed live to storage data")

            js.Draft6Validator(self._full_entity_schema).validate(data_store)
            LOGGER.info("Checked new storage structure")

            yaml.dump(data_store, shard_file)
            LOGGER.info("Saved storage")

    def _full_storage_form_to_entity(self, full_storage_form: JSONDictType) -> EntityRowType:
        entity = self._protocol.storage_to_live(full_storage_form)
        entity.ref_id = EntityId(typing.cast(str, full_storage_form["ref_id"]))
        entity.created_time = \
            Timestamp.from_str(typing.cast(str, full_storage_form["created_time"]))
        entity.last_modified_time = \
            Timestamp.from_str(typing.cast(str, full_storage_form["last_modified_time"]))
        entity.archived_time = \
            Timestamp.from_str(typing.cast(str, full_storage_form["archived_time"])) \
                if full_storage_form["archived_time"] is not None else None
        return entity

    def _entity_to_full_storage_form(self, entity: EntityRowType) -> JSONDictType:
        full_storage_form: JSONDictType = {
            "ref_id": str(entity.ref_id),
            "archived": entity.archived,
            "created_time": str(entity.created_time),
            "last_modified_time": str(entity.last_modified_time),
            "archived_time": str(entity.archived_time)
                             if entity.archived_time else None
        }
        for key, val in self._protocol.live_to_storage(entity).items():
            full_storage_form[key] = val
        return full_storage_form

    def _get_shard_id(self, ref_id: EntityId) -> int:
        hasher = hashlib.sha256()
        hasher.update(str(ref_id).encode("utf-8"))
        return int(hasher.hexdigest(), 16) % self._num_shards

    def _get_all_shard_ids(self) -> Iterable[int]:
        return range(0, self._num_shards)

    def _get_metadata_path(self) -> Path:
        return self._path / "metadata.yaml"

    def _get_shard_path(self, shard_id: int) -> Path:
        return self._path / f"shard-{shard_id}.yaml"
