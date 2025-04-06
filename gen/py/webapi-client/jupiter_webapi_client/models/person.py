from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.person_relationship import PersonRelationship
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.recurring_task_gen_params import RecurringTaskGenParams


T = TypeVar("T", bound="Person")


@_attrs_define
class Person:
    """A person.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The person name.
        person_collection_ref_id (str):
        relationship (PersonRelationship): The relationship the user has with a person.
        archived_time (Union[None, Unset, str]):
        catch_up_params (Union['RecurringTaskGenParams', None, Unset]):
        birthday (Union[None, Unset, str]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    person_collection_ref_id: str
    relationship: PersonRelationship
    archived_time: Union[None, Unset, str] = UNSET
    catch_up_params: Union["RecurringTaskGenParams", None, Unset] = UNSET
    birthday: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.recurring_task_gen_params import RecurringTaskGenParams

        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        person_collection_ref_id = self.person_collection_ref_id

        relationship = self.relationship.value

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        catch_up_params: Union[None, Unset, dict[str, Any]]
        if isinstance(self.catch_up_params, Unset):
            catch_up_params = UNSET
        elif isinstance(self.catch_up_params, RecurringTaskGenParams):
            catch_up_params = self.catch_up_params.to_dict()
        else:
            catch_up_params = self.catch_up_params

        birthday: Union[None, Unset, str]
        if isinstance(self.birthday, Unset):
            birthday = UNSET
        else:
            birthday = self.birthday

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "person_collection_ref_id": person_collection_ref_id,
                "relationship": relationship,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if catch_up_params is not UNSET:
            field_dict["catch_up_params"] = catch_up_params
        if birthday is not UNSET:
            field_dict["birthday"] = birthday

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.recurring_task_gen_params import RecurringTaskGenParams

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        person_collection_ref_id = d.pop("person_collection_ref_id")

        relationship = PersonRelationship(d.pop("relationship"))

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_catch_up_params(data: object) -> Union["RecurringTaskGenParams", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                catch_up_params_type_0 = RecurringTaskGenParams.from_dict(data)

                return catch_up_params_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RecurringTaskGenParams", None, Unset], data)

        catch_up_params = _parse_catch_up_params(d.pop("catch_up_params", UNSET))

        def _parse_birthday(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        birthday = _parse_birthday(d.pop("birthday", UNSET))

        person = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            person_collection_ref_id=person_collection_ref_id,
            relationship=relationship,
            archived_time=archived_time,
            catch_up_params=catch_up_params,
            birthday=birthday,
        )

        person.additional_properties = d
        return person

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
