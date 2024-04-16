from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

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
        person_collection (str):
        relationship (PersonRelationship): The relationship the user has with a person.
        archived_time (Union[Unset, str]): A timestamp in the application.
        catch_up_params (Union[Unset, RecurringTaskGenParams]): Parameters for metric collection.
        birthday (Union[Unset, str]): The birthday of a person.
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    person_collection: str
    relationship: PersonRelationship
    archived_time: Union[Unset, str] = UNSET
    catch_up_params: Union[Unset, "RecurringTaskGenParams"] = UNSET
    birthday: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        person_collection = self.person_collection

        relationship = self.relationship.value

        archived_time = self.archived_time

        catch_up_params: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.catch_up_params, Unset):
            catch_up_params = self.catch_up_params.to_dict()

        birthday = self.birthday

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "person_collection": person_collection,
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
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.recurring_task_gen_params import RecurringTaskGenParams

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        person_collection = d.pop("person_collection")

        relationship = PersonRelationship(d.pop("relationship"))

        archived_time = d.pop("archived_time", UNSET)

        _catch_up_params = d.pop("catch_up_params", UNSET)
        catch_up_params: Union[Unset, RecurringTaskGenParams]
        if isinstance(_catch_up_params, Unset):
            catch_up_params = UNSET
        else:
            catch_up_params = RecurringTaskGenParams.from_dict(_catch_up_params)

        birthday = d.pop("birthday", UNSET)

        person = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            person_collection=person_collection,
            relationship=relationship,
            archived_time=archived_time,
            catch_up_params=catch_up_params,
            birthday=birthday,
        )

        person.additional_properties = d
        return person

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
