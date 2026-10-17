from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.life_plan_eval_approach import LifePlanEvalApproach
from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.life_plan_eval_task_generation_in_advance_days import LifePlanEvalTaskGenerationInAdvanceDays
    from ..models.recurring_task_gen_params import RecurringTaskGenParams
    from ..models.scheduling_params import SchedulingParams


T = TypeVar("T", bound="LifePlan")


@_attrs_define
class LifePlan:
    """A aspect collection.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        workspace_ref_id (str):
        birthday (str): The birthday of a person.
        birth_year (int): The birth year of a person.
        max_age (int):
        time_plan_max_life_plan_links (int):
        eval_approach (LifePlanEvalApproach): The approach to generate life plan eval tasks.
        eval_periods (list[RecurringTaskPeriod]):
        eval_task_scheduling_params (SchedulingParams): Parameters for scheduling the work an entity generates.
        eval_task_generation_in_advance_days (LifePlanEvalTaskGenerationInAdvanceDays):
        archival_reason (None | str | Unset):
        archived_time (None | str | Unset):
        eval_task_gen_params (None | RecurringTaskGenParams | Unset):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    workspace_ref_id: str
    birthday: str
    birth_year: int
    max_age: int
    time_plan_max_life_plan_links: int
    eval_approach: LifePlanEvalApproach
    eval_periods: list[RecurringTaskPeriod]
    eval_task_scheduling_params: SchedulingParams
    eval_task_generation_in_advance_days: LifePlanEvalTaskGenerationInAdvanceDays
    archival_reason: None | str | Unset = UNSET
    archived_time: None | str | Unset = UNSET
    eval_task_gen_params: None | RecurringTaskGenParams | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.recurring_task_gen_params import RecurringTaskGenParams  # noqa: PLC0415

        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        workspace_ref_id = self.workspace_ref_id

        birthday = self.birthday

        birth_year = self.birth_year

        max_age = self.max_age

        time_plan_max_life_plan_links = self.time_plan_max_life_plan_links

        eval_approach = self.eval_approach.value

        eval_periods = []
        for eval_periods_item_data in self.eval_periods:
            eval_periods_item = eval_periods_item_data.value
            eval_periods.append(eval_periods_item)

        eval_task_scheduling_params = self.eval_task_scheduling_params.to_dict()

        eval_task_generation_in_advance_days = self.eval_task_generation_in_advance_days.to_dict()

        archival_reason: None | str | Unset
        if isinstance(self.archival_reason, Unset):
            archival_reason = UNSET
        else:
            archival_reason = self.archival_reason

        archived_time: None | str | Unset
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        eval_task_gen_params: dict[str, Any] | None | Unset
        if isinstance(self.eval_task_gen_params, Unset):
            eval_task_gen_params = UNSET
        elif isinstance(self.eval_task_gen_params, RecurringTaskGenParams):
            eval_task_gen_params = self.eval_task_gen_params.to_dict()
        else:
            eval_task_gen_params = self.eval_task_gen_params

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "workspace_ref_id": workspace_ref_id,
                "birthday": birthday,
                "birth_year": birth_year,
                "max_age": max_age,
                "time_plan_max_life_plan_links": time_plan_max_life_plan_links,
                "eval_approach": eval_approach,
                "eval_periods": eval_periods,
                "eval_task_scheduling_params": eval_task_scheduling_params,
                "eval_task_generation_in_advance_days": eval_task_generation_in_advance_days,
            }
        )
        if archival_reason is not UNSET:
            field_dict["archival_reason"] = archival_reason
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if eval_task_gen_params is not UNSET:
            field_dict["eval_task_gen_params"] = eval_task_gen_params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.life_plan_eval_task_generation_in_advance_days import LifePlanEvalTaskGenerationInAdvanceDays  # noqa: PLC0415
        from ..models.recurring_task_gen_params import RecurringTaskGenParams  # noqa: PLC0415
        from ..models.scheduling_params import SchedulingParams  # noqa: PLC0415

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        workspace_ref_id = d.pop("workspace_ref_id")

        birthday = d.pop("birthday")

        birth_year = d.pop("birth_year")

        max_age = d.pop("max_age")

        time_plan_max_life_plan_links = d.pop("time_plan_max_life_plan_links")

        eval_approach = LifePlanEvalApproach(d.pop("eval_approach"))

        eval_periods = []
        _eval_periods = d.pop("eval_periods")
        for eval_periods_item_data in _eval_periods:
            eval_periods_item = RecurringTaskPeriod(eval_periods_item_data)

            eval_periods.append(eval_periods_item)

        eval_task_scheduling_params = SchedulingParams.from_dict(d.pop("eval_task_scheduling_params"))

        eval_task_generation_in_advance_days = LifePlanEvalTaskGenerationInAdvanceDays.from_dict(
            d.pop("eval_task_generation_in_advance_days")
        )

        def _parse_archival_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        archival_reason = _parse_archival_reason(d.pop("archival_reason", UNSET))

        def _parse_archived_time(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_eval_task_gen_params(data: object) -> None | RecurringTaskGenParams | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                eval_task_gen_params_type_0 = RecurringTaskGenParams.from_dict(data)

                return eval_task_gen_params_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RecurringTaskGenParams | Unset, data)

        eval_task_gen_params = _parse_eval_task_gen_params(d.pop("eval_task_gen_params", UNSET))

        life_plan = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            workspace_ref_id=workspace_ref_id,
            birthday=birthday,
            birth_year=birth_year,
            max_age=max_age,
            time_plan_max_life_plan_links=time_plan_max_life_plan_links,
            eval_approach=eval_approach,
            eval_periods=eval_periods,
            eval_task_scheduling_params=eval_task_scheduling_params,
            eval_task_generation_in_advance_days=eval_task_generation_in_advance_days,
            archival_reason=archival_reason,
            archived_time=archived_time,
            eval_task_gen_params=eval_task_gen_params,
        )

        life_plan.additional_properties = d
        return life_plan

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
