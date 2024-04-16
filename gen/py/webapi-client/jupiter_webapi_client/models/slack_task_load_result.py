from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask
    from ..models.slack_task import SlackTask


T = TypeVar("T", bound="SlackTaskLoadResult")


@_attrs_define
class SlackTaskLoadResult:
    """SlackTaskLoadResult.

    Attributes:
        slack_task (SlackTask): A Slack task which needs to be converted into an inbox task.
        inbox_task (Union[Unset, InboxTask]): An inbox task.
    """

    slack_task: "SlackTask"
    inbox_task: Union[Unset, "InboxTask"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        slack_task = self.slack_task.to_dict()

        inbox_task: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.inbox_task, Unset):
            inbox_task = self.inbox_task.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "slack_task": slack_task,
            }
        )
        if inbox_task is not UNSET:
            field_dict["inbox_task"] = inbox_task

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.slack_task import SlackTask

        d = src_dict.copy()
        slack_task = SlackTask.from_dict(d.pop("slack_task"))

        _inbox_task = d.pop("inbox_task", UNSET)
        inbox_task: Union[Unset, InboxTask]
        if isinstance(_inbox_task, Unset):
            inbox_task = UNSET
        else:
            inbox_task = InboxTask.from_dict(_inbox_task)

        slack_task_load_result = cls(
            slack_task=slack_task,
            inbox_task=inbox_task,
        )

        slack_task_load_result.additional_properties = d
        return slack_task_load_result

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
