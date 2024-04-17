from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.record_score_result import RecordScoreResult


T = TypeVar("T", bound="BigPlanUpdateResult")


@_attrs_define
class BigPlanUpdateResult:
    """InboxTaskUpdate result.

    Attributes:
        record_score_result (Union['RecordScoreResult', None, Unset]):
    """

    record_score_result: Union["RecordScoreResult", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.record_score_result import RecordScoreResult

        record_score_result: Union[Dict[str, Any], None, Unset]
        if isinstance(self.record_score_result, Unset):
            record_score_result = UNSET
        elif isinstance(self.record_score_result, RecordScoreResult):
            record_score_result = self.record_score_result.to_dict()
        else:
            record_score_result = self.record_score_result

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

        def _parse_record_score_result(data: object) -> Union["RecordScoreResult", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                record_score_result_type_0 = RecordScoreResult.from_dict(data)

                return record_score_result_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RecordScoreResult", None, Unset], data)

        record_score_result = _parse_record_score_result(d.pop("record_score_result", UNSET))

        big_plan_update_result = cls(
            record_score_result=record_score_result,
        )

        big_plan_update_result.additional_properties = d
        return big_plan_update_result

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
