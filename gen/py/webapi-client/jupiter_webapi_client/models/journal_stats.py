from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.report_period_result import ReportPeriodResult


T = TypeVar("T", bound="JournalStats")


@_attrs_define
class JournalStats:
    """Stats about a journal.

    Attributes:
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        journal_ref_id (str):
        report (ReportPeriodResult): Report result.
    """

    created_time: str
    last_modified_time: str
    journal_ref_id: str
    report: "ReportPeriodResult"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_time = self.created_time

        last_modified_time = self.last_modified_time

        journal_ref_id = self.journal_ref_id

        report = self.report.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "journal_ref_id": journal_ref_id,
                "report": report,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.report_period_result import ReportPeriodResult

        d = dict(src_dict)
        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        journal_ref_id = d.pop("journal_ref_id")

        report = ReportPeriodResult.from_dict(d.pop("report"))

        journal_stats = cls(
            created_time=created_time,
            last_modified_time=last_modified_time,
            journal_ref_id=journal_ref_id,
            report=report,
        )

        journal_stats.additional_properties = d
        return journal_stats

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
