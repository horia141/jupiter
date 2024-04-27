from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask
    from ..models.note import Note
    from ..models.person import Person


T = TypeVar("T", bound="PersonFindResultEntry")


@_attrs_define
class PersonFindResultEntry:
    """A single person result.

    Attributes:
        person (Person): A person.
        note (Union['Note', None, Unset]):
        catch_up_inbox_tasks (Union[List['InboxTask'], None, Unset]):
        birthday_inbox_tasks (Union[List['InboxTask'], None, Unset]):
    """

    person: "Person"
    note: Union["Note", None, Unset] = UNSET
    catch_up_inbox_tasks: Union[List["InboxTask"], None, Unset] = UNSET
    birthday_inbox_tasks: Union[List["InboxTask"], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.note import Note

        person = self.person.to_dict()

        note: Union[Dict[str, Any], None, Unset]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        catch_up_inbox_tasks: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.catch_up_inbox_tasks, Unset):
            catch_up_inbox_tasks = UNSET
        elif isinstance(self.catch_up_inbox_tasks, list):
            catch_up_inbox_tasks = []
            for catch_up_inbox_tasks_type_0_item_data in self.catch_up_inbox_tasks:
                catch_up_inbox_tasks_type_0_item = catch_up_inbox_tasks_type_0_item_data.to_dict()
                catch_up_inbox_tasks.append(catch_up_inbox_tasks_type_0_item)

        else:
            catch_up_inbox_tasks = self.catch_up_inbox_tasks

        birthday_inbox_tasks: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.birthday_inbox_tasks, Unset):
            birthday_inbox_tasks = UNSET
        elif isinstance(self.birthday_inbox_tasks, list):
            birthday_inbox_tasks = []
            for birthday_inbox_tasks_type_0_item_data in self.birthday_inbox_tasks:
                birthday_inbox_tasks_type_0_item = birthday_inbox_tasks_type_0_item_data.to_dict()
                birthday_inbox_tasks.append(birthday_inbox_tasks_type_0_item)

        else:
            birthday_inbox_tasks = self.birthday_inbox_tasks

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "person": person,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if catch_up_inbox_tasks is not UNSET:
            field_dict["catch_up_inbox_tasks"] = catch_up_inbox_tasks
        if birthday_inbox_tasks is not UNSET:
            field_dict["birthday_inbox_tasks"] = birthday_inbox_tasks

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.note import Note
        from ..models.person import Person

        d = src_dict.copy()
        person = Person.from_dict(d.pop("person"))

        def _parse_note(data: object) -> Union["Note", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                note_type_0 = Note.from_dict(data)

                return note_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Note", None, Unset], data)

        note = _parse_note(d.pop("note", UNSET))

        def _parse_catch_up_inbox_tasks(data: object) -> Union[List["InboxTask"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                catch_up_inbox_tasks_type_0 = []
                _catch_up_inbox_tasks_type_0 = data
                for catch_up_inbox_tasks_type_0_item_data in _catch_up_inbox_tasks_type_0:
                    catch_up_inbox_tasks_type_0_item = InboxTask.from_dict(catch_up_inbox_tasks_type_0_item_data)

                    catch_up_inbox_tasks_type_0.append(catch_up_inbox_tasks_type_0_item)

                return catch_up_inbox_tasks_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["InboxTask"], None, Unset], data)

        catch_up_inbox_tasks = _parse_catch_up_inbox_tasks(d.pop("catch_up_inbox_tasks", UNSET))

        def _parse_birthday_inbox_tasks(data: object) -> Union[List["InboxTask"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                birthday_inbox_tasks_type_0 = []
                _birthday_inbox_tasks_type_0 = data
                for birthday_inbox_tasks_type_0_item_data in _birthday_inbox_tasks_type_0:
                    birthday_inbox_tasks_type_0_item = InboxTask.from_dict(birthday_inbox_tasks_type_0_item_data)

                    birthday_inbox_tasks_type_0.append(birthday_inbox_tasks_type_0_item)

                return birthday_inbox_tasks_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["InboxTask"], None, Unset], data)

        birthday_inbox_tasks = _parse_birthday_inbox_tasks(d.pop("birthday_inbox_tasks", UNSET))

        person_find_result_entry = cls(
            person=person,
            note=note,
            catch_up_inbox_tasks=catch_up_inbox_tasks,
            birthday_inbox_tasks=birthday_inbox_tasks,
        )

        person_find_result_entry.additional_properties = d
        return person_find_result_entry

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
