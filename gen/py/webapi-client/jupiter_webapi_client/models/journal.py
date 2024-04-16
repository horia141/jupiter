from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.journal_source import JournalSource
from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.report_period_result import ReportPeriodResult


T = TypeVar("T", bound="Journal")


@_attrs_define
class Journal:
    """A journal for a particular range.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name for an entity which acts as both name and unique identifier.
        journal_collection (str):
        source (JournalSource): The source of a journal entry.
        right_now (str): A date or possibly a datetime for the application.
        period (RecurringTaskPeriod): A period for a particular task.
        timeline (str):
        report (ReportPeriodResult): Report result.
        archived_time (Union[Unset, str]): A timestamp in the application.
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    journal_collection: str
    source: JournalSource
    right_now: str
    period: RecurringTaskPeriod
    timeline: str
    report: "ReportPeriodResult"
    archived_time: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        journal_collection = self.journal_collection

        source = self.source.value

        right_now = self.right_now

        period = self.period.value

        timeline = self.timeline

        report = self.report.to_dict()

        archived_time = self.archived_time

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "journal_collection": journal_collection,
                "source": source,
                "right_now": right_now,
                "period": period,
                "timeline": timeline,
                "report": report,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.report_period_result import ReportPeriodResult

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        journal_collection = d.pop("journal_collection")

        source = JournalSource(d.pop("source"))

        right_now = d.pop("right_now")

        period = RecurringTaskPeriod(d.pop("period"))

        timeline = d.pop("timeline")

        report = ReportPeriodResult.from_dict(d.pop("report"))

        archived_time = d.pop("archived_time", UNSET)

        journal = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            journal_collection=journal_collection,
            source=source,
            right_now=right_now,
            period=period,
            timeline=timeline,
            report=report,
            archived_time=archived_time,
        )

        journal.additional_properties = d
        return journal

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
