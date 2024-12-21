from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask


T = TypeVar("T", bound="BigPlanArchiveServiceResult")


@_attrs_define
class BigPlanArchiveServiceResult:
    """The result of the archive operation.

    Attributes:
        archived_inbox_tasks (List['InboxTask']):
    """

    archived_inbox_tasks: List["InboxTask"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        archived_inbox_tasks = []
        for archived_inbox_tasks_item_data in self.archived_inbox_tasks:
            archived_inbox_tasks_item = archived_inbox_tasks_item_data.to_dict()
            archived_inbox_tasks.append(archived_inbox_tasks_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "archived_inbox_tasks": archived_inbox_tasks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_task import InboxTask

        d = src_dict.copy()
        archived_inbox_tasks = []
        _archived_inbox_tasks = d.pop("archived_inbox_tasks")
        for archived_inbox_tasks_item_data in _archived_inbox_tasks:
            archived_inbox_tasks_item = InboxTask.from_dict(archived_inbox_tasks_item_data)

            archived_inbox_tasks.append(archived_inbox_tasks_item)

        big_plan_archive_service_result = cls(
            archived_inbox_tasks=archived_inbox_tasks,
        )

        big_plan_archive_service_result.additional_properties = d
        return big_plan_archive_service_result

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
