"""Application-specific realm helpers."""
import importlib
import pkgutil
from types import GenericAlias, ModuleType
from typing import Generic, Iterator, TypeVar, cast, get_args, get_origin

from jupiter.core.framework.concept import Concept
from jupiter.core.framework.entity import Entity
from jupiter.core.framework.realm import (
    DatabaseRealm,
    Realm,
    RealmCodecRegistry,
    RealmConcept,
    RealmDecoder,
    RealmDecodingError,
    RealmEncoder,
)
from jupiter.core.framework.value import AtomicValue, EnumValue
from pendulum.date import Date
from pendulum.datetime import DateTime

_RealmT = TypeVar("_RealmT", bound=Realm)
_ConceptT = TypeVar("_ConceptT", bound=Concept)
_AtomicValueT = TypeVar("_AtomicValueT", bound=AtomicValue)
_EnumValueT = TypeVar("_EnumValueT", bound=EnumValue)


class _StandardAtomicValueDatabaseEncoder(
    Generic[_AtomicValueT], RealmEncoder[_AtomicValueT, DatabaseRealm]
):

    _the_type: type[_AtomicValueT]

    def __init__(self, the_type: type[_AtomicValueT]) -> None:
        """Initialize the encoder."""
        self._the_type = the_type

    def encode(self, value: _AtomicValueT) -> RealmConcept:
        """Encode a realm to a string."""
        return value.to_primitive()


class _StandardAtomicValueDatabaseDecoder(
    Generic[_AtomicValueT], RealmDecoder[_AtomicValueT, DatabaseRealm]
):
    """A codec for atomic values."""

    _the_type: type[_AtomicValueT]

    def __init__(self, the_type: type[_AtomicValueT]) -> None:
        self._the_type = the_type

    def decode(self, value: RealmConcept) -> _AtomicValueT:
        """Decode a realm from a string."""
        if not isinstance(value, (type(None), bool, int, float, str, Date, DateTime)):
            raise Exception(
                f"Expected value for {self._the_type.__name__} in {self.__class__} to be primitive"
            )

        return self._the_type.from_raw(value)


class _StandardEnumValueDatabaseEncoder(
    Generic[_EnumValueT], RealmEncoder[_EnumValueT, DatabaseRealm]
):

    _the_type: type[_EnumValueT]

    def __init__(self, the_type: type[_EnumValueT]) -> None:
        """Initialize the encoder."""
        self._the_type = the_type

    def encode(self, value: _EnumValueT) -> RealmConcept:
        """Encode a realm to a string."""
        return str(value.value)


class _StandardEnumValueDatabaseDecoder(
    Generic[_EnumValueT], RealmDecoder[_EnumValueT, DatabaseRealm]
):
    """A codec for enums."""

    _the_type: type[_EnumValueT]

    def __init__(self, the_type: type[_EnumValueT]) -> None:
        """Initialize the encoder."""
        self._the_type = the_type

    def decode(self, value: RealmConcept) -> _EnumValueT:
        """Decode a realm from a string."""
        if not isinstance(value, str):
            raise RealmDecodingError(
                f"Expected value for {self._the_type.__name__} to be string"
            )

        value_clean: str = value.strip().lower()

        try:
            return cast(_EnumValueT, self._the_type(value_clean))
        except ValueError:
            raise RealmDecodingError(
                f"Expected enum {self._the_type.__name__} '{value}' to be one of '{','.join(str(s.value) for s in self._the_type)}'",
            ) from None


class ModuleExplorerRealmCodecRegistry(RealmCodecRegistry):
    """A registry for realm codecs constructed by exploring a module tree."""

    _encoders_registry: dict[
        tuple[type[Concept], type[Realm]], RealmEncoder[Concept, Realm]
    ]
    _decoders_registry: dict[
        tuple[type[Concept], type[Realm]], RealmDecoder[Concept, Realm]
    ]

    def __init__(
        self,
        encoders_registry: dict[
            tuple[type[Concept], type[Realm]], RealmEncoder[Concept, Realm]
        ],
        decoders_registry: dict[
            tuple[type[Concept], type[Realm]], RealmDecoder[Concept, Realm]
        ],
    ) -> None:
        """Initialize the registry."""
        self._encoders_registry = encoders_registry
        self._decoders_registry = decoders_registry

    @staticmethod
    def build_from_module_root(
        module_root: ModuleType,
    ) -> "ModuleExplorerRealmCodecRegistry":
        """Build a registry from a module root using magick."""

        def find_all_modules() -> list[ModuleType]:
            all_modules = []

            def explore_module_tree(the_module: ModuleType) -> None:
                for _, name, is_pkg in pkgutil.iter_modules(the_module.__path__):
                    full_name = the_module.__name__ + "." + name
                    all_modules.append(importlib.import_module(full_name))
                    if is_pkg:
                        submodule = getattr(the_module, name)
                        explore_module_tree(submodule)

            explore_module_tree(module_root)
            return all_modules

        def extract_atomic_values(
            the_module: ModuleType,
        ) -> Iterator[type[AtomicValue]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, AtomicValue)):
                    continue

                yield obj

        def extract_enum_values(
            the_module: ModuleType,
        ) -> Iterator[type[EnumValue]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, EnumValue)):
                    continue

                yield obj

        def extract_entities(
            the_module: ModuleType,
        ) -> Iterator[type[Entity]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, Entity)):
                    continue

                yield obj

        def figure_out_realm(the_type: type) -> type[Realm] | None:
            if not hasattr(the_type, "__orig_bases__"):
                return None

            for base in the_type.__orig_bases__:
                base_args = get_args(base)
                if len(base_args) == 0:
                    continue
                for base_arg in base_args:
                    if isinstance(base_arg, type) and issubclass(base_arg, Realm):
                        return base_arg

                origin_base = cast(type | GenericAlias, get_origin(base))
                if origin_base != base:
                    possible_concept_type = figure_out_realm(
                        cast(type, origin_base)
                    )  # We know better!
                    if possible_concept_type is not None:
                        return possible_concept_type

            return None

        def figure_out_concept(the_type: type) -> type[Concept] | None:
            if not hasattr(the_type, "__orig_bases__"):
                return None

            for base in the_type.__orig_bases__:
                base_args = get_args(base)
                if len(base_args) == 0:
                    continue
                for base_arg in base_args:
                    if isinstance(base_arg, type) and issubclass(base_arg, Concept):
                        return base_arg

                origin_base = cast(type | GenericAlias, get_origin(base))
                if origin_base != base:
                    possible_concept_type = figure_out_concept(
                        cast(type, origin_base)
                    )  # We know better!
                    if possible_concept_type is not None:
                        return possible_concept_type

            return None

        def extract_realm_encoders(
            the_module: ModuleType,
        ) -> Iterator[
            tuple[type[Concept], type[Realm], type[RealmEncoder[Concept, Realm]]]
        ]:
            for name, obj in the_module.__dict__.items():
                if not hasattr(obj, "__parameters__"):
                    continue

                if len(obj.__parameters__) > 0:
                    # This is not a concret type and we can move on
                    continue

                if not (isinstance(obj, type) and issubclass(obj, RealmEncoder)):
                    continue

                concept_type = figure_out_concept(cast(type, obj))
                if concept_type is None:
                    raise Exception(
                        f"Could not infer concept class from encoder class {name} in {the_module.__name__} because inheritence is messed-up"
                    )
                realm_type = figure_out_realm(cast(type, obj))
                if realm_type is None:
                    raise Exception(
                        f"Could not infer realm class from encoder class {name} in {the_module.__name__} because inheritence is messed-up"
                    )

                yield concept_type, realm_type, cast(type, obj)

        def extract_realm_decoders(
            the_module: ModuleType,
        ) -> Iterator[
            tuple[type[Concept], type[Realm], type[RealmDecoder[Concept, Realm]]]
        ]:
            for name, obj in the_module.__dict__.items():
                if not hasattr(obj, "__parameters__"):
                    continue

                if len(obj.__parameters__) > 0:
                    # This is not a concret type and we can move on
                    continue

                if not (isinstance(obj, type) and issubclass(obj, RealmDecoder)):
                    continue

                concept_type = figure_out_concept(cast(type, obj))
                if concept_type is None:
                    raise Exception(
                        f"Could not infer concept class from decoder class {name} in {the_module.__name__} because inheritence is messed-up"
                    )
                realm_type = figure_out_realm(cast(type, obj))
                if realm_type is None:
                    raise Exception(
                        f"Could not infer realm class from decoder class {name} in {the_module.__name__} because inheritence is messed-up"
                    )

                yield concept_type, realm_type, cast(type, obj)

        encoders_registry: dict[
            tuple[type[Concept], type[Realm]], RealmEncoder[Concept, Realm]
        ] = {}
        decoders_registry: dict[
            tuple[type[Concept], type[Realm]], RealmDecoder[Concept, Realm]
        ] = {}

        # registry._add_codec(DatabaseRealm, EntityId, EntityIdDatabaseCodec())
        # registry._add_codec(DatabaseRealm, Timestamp, TimestampDatabaseCodec())

        for m in find_all_modules():
            for concept_type, realm_type, encoder_type in extract_realm_encoders(m):
                if (concept_type, realm_type) in encoders_registry:
                    raise Exception(
                        f"Duplicate encoder for realm {realm_type} and concept {concept_type.__name__}"
                    )
                encoders_registry[(concept_type, realm_type)] = cast(
                    RealmEncoder[Concept, Realm], encoder_type()
                )

            for concept_type, realm_type, decoder_type in extract_realm_decoders(m):
                if (concept_type, realm_type) in encoders_registry:
                    raise Exception(
                        f"Duplicate decoder for realm {realm_type} and concept {concept_type.__name__}"
                    )
                decoders_registry[(concept_type, realm_type)] = cast(
                    RealmDecoder[Concept, Realm], decoder_type()
                )

            for atomic_value_type in extract_atomic_values(m):
                if (atomic_value_type, DatabaseRealm) not in encoders_registry:
                    encoders_registry[(atomic_value_type, DatabaseRealm)] = cast(
                        RealmEncoder[Concept, Realm],
                        _StandardAtomicValueDatabaseEncoder(atomic_value_type),
                    )

                if (atomic_value_type, DatabaseRealm) not in decoders_registry:
                    decoders_registry[(atomic_value_type, DatabaseRealm)] = cast(
                        RealmDecoder[Concept, Realm],
                        _StandardAtomicValueDatabaseDecoder(atomic_value_type),
                    )

            for enum_value_type in extract_enum_values(m):
                if (enum_value_type, DatabaseRealm) not in encoders_registry:
                    encoders_registry[(enum_value_type, DatabaseRealm)] = cast(
                        RealmEncoder[Concept, Realm],
                        _StandardEnumValueDatabaseEncoder(enum_value_type),
                    )

                if (enum_value_type, DatabaseRealm) not in decoders_registry:
                    decoders_registry[(enum_value_type, DatabaseRealm)] = cast(
                        RealmDecoder[Concept, Realm],
                        _StandardEnumValueDatabaseDecoder(enum_value_type),
                    )

        registry = ModuleExplorerRealmCodecRegistry(
            encoders_registry, decoders_registry
        )

        return registry

    def get_encoder(
        self,
        concept_type: type[_ConceptT],
        realm: type[_RealmT],
    ) -> RealmEncoder[_ConceptT, _RealmT]:
        """Get a codec for a realm and a concept type."""
        if (concept_type, realm) not in self._encoders_registry:
            raise Exception(
                f"Could not find encoder for realm {realm} and concept {concept_type.__name__}"
            )
        return cast(
            RealmEncoder[_ConceptT, _RealmT],
            self._encoders_registry[(concept_type, realm)],
        )

    def get_decoder(
        self,
        concept_type: type[_ConceptT],
        realm: type[_RealmT],
    ) -> RealmDecoder[_ConceptT, _RealmT]:
        """Get a codec for a realm and a concept type."""
        if (concept_type, realm) not in self._decoders_registry:
            raise Exception(
                f"Could not find decoder for realm {realm} and concept {concept_type.__name__}"
            )
        return cast(
            RealmDecoder[_ConceptT, _RealmT],
            self._decoders_registry[(concept_type, realm)],
        )
