from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask


T = TypeVar("T", bound="InboxTaskCreateResult")


@_attrs_define
class InboxTaskCreateResult:
    """InboxTaskCreate result.

    Attributes:
        new_inbox_task (InboxTask): An inbox task.
    """

    new_inbox_task: "InboxTask"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        new_inbox_task = self.new_inbox_task.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_inbox_task": new_inbox_task,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_task import InboxTask

        d = src_dict.copy()
        new_inbox_task = InboxTask.from_dict(d.pop("new_inbox_task"))

        inbox_task_create_result = cls(
            new_inbox_task=new_inbox_task,
        )

        inbox_task_create_result.additional_properties = d
        return inbox_task_create_result

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
