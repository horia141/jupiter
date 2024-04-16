from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

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
        inbox_task (Union[Unset, InboxTask]): An inbox task.
    """

    email_task: "EmailTask"
    inbox_task: Union[Unset, "InboxTask"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        email_task = self.email_task.to_dict()

        inbox_task: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.inbox_task, Unset):
            inbox_task = self.inbox_task.to_dict()

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

        _inbox_task = d.pop("inbox_task", UNSET)
        inbox_task: Union[Unset, InboxTask]
        if isinstance(_inbox_task, Unset):
            inbox_task = UNSET
        else:
            inbox_task = InboxTask.from_dict(_inbox_task)

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
