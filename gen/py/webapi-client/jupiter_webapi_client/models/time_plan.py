from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod
from ..models.time_plan_source import TimePlanSource
from ..types import UNSET, Unset

T = TypeVar("T", bound="TimePlan")


@_attrs_define
class TimePlan:
    """A plan for a particular period of time.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name for an entity which acts as both name and unique identifier.
        time_plan_domain_ref_id (str):
        source (TimePlanSource): The source of a time plan.
        right_now (str): A date or possibly a datetime for the application.
        period (RecurringTaskPeriod): A period for a particular task.
        timeline (str):
        start_date (str): A date or possibly a datetime for the application.
        end_date (str): A date or possibly a datetime for the application.
        archived_time (Union[None, Unset, str]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    time_plan_domain_ref_id: str
    source: TimePlanSource
    right_now: str
    period: RecurringTaskPeriod
    timeline: str
    start_date: str
    end_date: str
    archived_time: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        time_plan_domain_ref_id = self.time_plan_domain_ref_id

        source = self.source.value

        right_now = self.right_now

        period = self.period.value

        timeline = self.timeline

        start_date = self.start_date

        end_date = self.end_date

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "time_plan_domain_ref_id": time_plan_domain_ref_id,
                "source": source,
                "right_now": right_now,
                "period": period,
                "timeline": timeline,
                "start_date": start_date,
                "end_date": end_date,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        time_plan_domain_ref_id = d.pop("time_plan_domain_ref_id")

        source = TimePlanSource(d.pop("source"))

        right_now = d.pop("right_now")

        period = RecurringTaskPeriod(d.pop("period"))

        timeline = d.pop("timeline")

        start_date = d.pop("start_date")

        end_date = d.pop("end_date")

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        time_plan = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            time_plan_domain_ref_id=time_plan_domain_ref_id,
            source=source,
            right_now=right_now,
            period=period,
            timeline=timeline,
            start_date=start_date,
            end_date=end_date,
            archived_time=archived_time,
        )

        time_plan.additional_properties = d
        return time_plan

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
