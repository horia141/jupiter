from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.record_score_result import RecordScoreResult


T = TypeVar("T", bound="InboxTaskUpdateResult")


@_attrs_define
class InboxTaskUpdateResult:
    """InboxTaskUpdate result.

    Attributes:
        record_score_result (Union[Unset, RecordScoreResult]): The result of the score recording.
    """

    record_score_result: Union[Unset, "RecordScoreResult"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        record_score_result: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.record_score_result, Unset):
            record_score_result = self.record_score_result.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if record_score_result is not UNSET:
            field_dict["record_score_result"] = record_score_result

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.record_score_result import RecordScoreResult

        d = src_dict.copy()
        _record_score_result = d.pop("record_score_result", UNSET)
        record_score_result: Union[Unset, RecordScoreResult]
        if isinstance(_record_score_result, Unset):
            record_score_result = UNSET
        else:
            record_score_result = RecordScoreResult.from_dict(_record_score_result)

        inbox_task_update_result = cls(
            record_score_result=record_score_result,
        )

        inbox_task_update_result.additional_properties = d
        return inbox_task_update_result

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
