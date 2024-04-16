from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask
    from ..models.note import Note
    from ..models.person import Person


T = TypeVar("T", bound="PersonLoadResult")


@_attrs_define
class PersonLoadResult:
    """PersonLoadResult.

    Attributes:
        person (Person): A person.
        catch_up_inbox_tasks (List['InboxTask']):
        birthday_inbox_tasks (List['InboxTask']):
        note (Union[Unset, Note]): A note in the notebook.
    """

    person: "Person"
    catch_up_inbox_tasks: List["InboxTask"]
    birthday_inbox_tasks: List["InboxTask"]
    note: Union[Unset, "Note"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        person = self.person.to_dict()

        catch_up_inbox_tasks = []
        for catch_up_inbox_tasks_item_data in self.catch_up_inbox_tasks:
            catch_up_inbox_tasks_item = catch_up_inbox_tasks_item_data.to_dict()
            catch_up_inbox_tasks.append(catch_up_inbox_tasks_item)

        birthday_inbox_tasks = []
        for birthday_inbox_tasks_item_data in self.birthday_inbox_tasks:
            birthday_inbox_tasks_item = birthday_inbox_tasks_item_data.to_dict()
            birthday_inbox_tasks.append(birthday_inbox_tasks_item)

        note: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.note, Unset):
            note = self.note.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "person": person,
                "catch_up_inbox_tasks": catch_up_inbox_tasks,
                "birthday_inbox_tasks": birthday_inbox_tasks,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.note import Note
        from ..models.person import Person

        d = src_dict.copy()
        person = Person.from_dict(d.pop("person"))

        catch_up_inbox_tasks = []
        _catch_up_inbox_tasks = d.pop("catch_up_inbox_tasks")
        for catch_up_inbox_tasks_item_data in _catch_up_inbox_tasks:
            catch_up_inbox_tasks_item = InboxTask.from_dict(catch_up_inbox_tasks_item_data)

            catch_up_inbox_tasks.append(catch_up_inbox_tasks_item)

        birthday_inbox_tasks = []
        _birthday_inbox_tasks = d.pop("birthday_inbox_tasks")
        for birthday_inbox_tasks_item_data in _birthday_inbox_tasks:
            birthday_inbox_tasks_item = InboxTask.from_dict(birthday_inbox_tasks_item_data)

            birthday_inbox_tasks.append(birthday_inbox_tasks_item)

        _note = d.pop("note", UNSET)
        note: Union[Unset, Note]
        if isinstance(_note, Unset):
            note = UNSET
        else:
            note = Note.from_dict(_note)

        person_load_result = cls(
            person=person,
            catch_up_inbox_tasks=catch_up_inbox_tasks,
            birthday_inbox_tasks=birthday_inbox_tasks,
            note=note,
        )

        person_load_result.additional_properties = d
        return person_load_result

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
