from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.report_period_result import ReportPeriodResult


T = TypeVar("T", bound="ReportResult")


@_attrs_define
class ReportResult:
    """Report results.

    Attributes:
        period_result (ReportPeriodResult): Report result.
    """

    period_result: "ReportPeriodResult"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        period_result = self.period_result.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "period_result": period_result,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.report_period_result import ReportPeriodResult

        d = src_dict.copy()
        period_result = ReportPeriodResult.from_dict(d.pop("period_result"))

        report_result = cls(
            period_result=period_result,
        )

        report_result.additional_properties = d
        return report_result

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
