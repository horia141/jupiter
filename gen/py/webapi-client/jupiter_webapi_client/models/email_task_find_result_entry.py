from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.email_task import EmailTask
    from ..models.inbox_task import InboxTask


T = TypeVar("T", bound="EmailTaskFindResultEntry")


@_attrs_define
class EmailTaskFindResultEntry:
    """A single email task result.

    Attributes:
        email_task (EmailTask): An email task which needs to be converted into an inbox task.
        inbox_task (Union['InboxTask', None, Unset]):
    """

    email_task: "EmailTask"
    inbox_task: Union["InboxTask", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.inbox_task import InboxTask

        email_task = self.email_task.to_dict()

        inbox_task: Union[Dict[str, Any], None, Unset]
        if isinstance(self.inbox_task, Unset):
            inbox_task = UNSET
        elif isinstance(self.inbox_task, InboxTask):
            inbox_task = self.inbox_task.to_dict()
        else:
            inbox_task = self.inbox_task

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email_task": email_task,
            }
        )
        if inbox_task is not UNSET:
            field_dict["inbox_task"] = inbox_task

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.email_task import EmailTask
        from ..models.inbox_task import InboxTask

        d = src_dict.copy()
        email_task = EmailTask.from_dict(d.pop("email_task"))

        def _parse_inbox_task(data: object) -> Union["InboxTask", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                inbox_task_type_0 = InboxTask.from_dict(data)

                return inbox_task_type_0
            except:  # noqa: E722
                pass
            return cast(Union["InboxTask", None, Unset], data)

        inbox_task = _parse_inbox_task(d.pop("inbox_task", UNSET))

        email_task_find_result_entry = cls(
            email_task=email_task,
            inbox_task=inbox_task,
        )

        email_task_find_result_entry.additional_properties = d
        return email_task_find_result_entry

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
