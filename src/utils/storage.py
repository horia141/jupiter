"""Some storage utils."""

import logging
from pathlib import Path
from typing import Final, Dict, Any, Protocol, TypeVar, Generic, Optional, List, Tuple, Union, Iterable

import jsonschema as js
import yaml


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
