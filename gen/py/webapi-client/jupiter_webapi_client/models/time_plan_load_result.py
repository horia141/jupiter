from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.big_plan import BigPlan
    from ..models.inbox_task import InboxTask
    from ..models.note import Note
    from ..models.time_plan import TimePlan
    from ..models.time_plan_activity import TimePlanActivity


T = TypeVar("T", bound="TimePlanLoadResult")


@_attrs_define
class TimePlanLoadResult:
    """Result.

    Attributes:
        time_plan (TimePlan): A plan for a particular period of time.
        note (Note): A note in the notebook.
        activities (List['TimePlanActivity']):
        target_inbox_tasks (List['InboxTask']):
        completed_nontarget_inbox_tasks (List['InboxTask']):
        sub_period_time_plans (List['TimePlan']):
        target_big_plans (Union[List['BigPlan'], None, Unset]):
        completed_nottarget_big_plans (Union[List['BigPlan'], None, Unset]):
        higher_time_plan (Union['TimePlan', None, Unset]):
        previous_time_plan (Union['TimePlan', None, Unset]):
    """

    time_plan: "TimePlan"
    note: "Note"
    activities: List["TimePlanActivity"]
    target_inbox_tasks: List["InboxTask"]
    completed_nontarget_inbox_tasks: List["InboxTask"]
    sub_period_time_plans: List["TimePlan"]
    target_big_plans: Union[List["BigPlan"], None, Unset] = UNSET
    completed_nottarget_big_plans: Union[List["BigPlan"], None, Unset] = UNSET
    higher_time_plan: Union["TimePlan", None, Unset] = UNSET
    previous_time_plan: Union["TimePlan", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.time_plan import TimePlan

        time_plan = self.time_plan.to_dict()

        note = self.note.to_dict()

        activities = []
        for activities_item_data in self.activities:
            activities_item = activities_item_data.to_dict()
            activities.append(activities_item)

        target_inbox_tasks = []
        for target_inbox_tasks_item_data in self.target_inbox_tasks:
            target_inbox_tasks_item = target_inbox_tasks_item_data.to_dict()
            target_inbox_tasks.append(target_inbox_tasks_item)

        completed_nontarget_inbox_tasks = []
        for completed_nontarget_inbox_tasks_item_data in self.completed_nontarget_inbox_tasks:
            completed_nontarget_inbox_tasks_item = completed_nontarget_inbox_tasks_item_data.to_dict()
            completed_nontarget_inbox_tasks.append(completed_nontarget_inbox_tasks_item)

        sub_period_time_plans = []
        for sub_period_time_plans_item_data in self.sub_period_time_plans:
            sub_period_time_plans_item = sub_period_time_plans_item_data.to_dict()
            sub_period_time_plans.append(sub_period_time_plans_item)

        target_big_plans: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.target_big_plans, Unset):
            target_big_plans = UNSET
        elif isinstance(self.target_big_plans, list):
            target_big_plans = []
            for target_big_plans_type_0_item_data in self.target_big_plans:
                target_big_plans_type_0_item = target_big_plans_type_0_item_data.to_dict()
                target_big_plans.append(target_big_plans_type_0_item)

        else:
            target_big_plans = self.target_big_plans

        completed_nottarget_big_plans: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.completed_nottarget_big_plans, Unset):
            completed_nottarget_big_plans = UNSET
        elif isinstance(self.completed_nottarget_big_plans, list):
            completed_nottarget_big_plans = []
            for completed_nottarget_big_plans_type_0_item_data in self.completed_nottarget_big_plans:
                completed_nottarget_big_plans_type_0_item = completed_nottarget_big_plans_type_0_item_data.to_dict()
                completed_nottarget_big_plans.append(completed_nottarget_big_plans_type_0_item)

        else:
            completed_nottarget_big_plans = self.completed_nottarget_big_plans

        higher_time_plan: Union[Dict[str, Any], None, Unset]
        if isinstance(self.higher_time_plan, Unset):
            higher_time_plan = UNSET
        elif isinstance(self.higher_time_plan, TimePlan):
            higher_time_plan = self.higher_time_plan.to_dict()
        else:
            higher_time_plan = self.higher_time_plan

        previous_time_plan: Union[Dict[str, Any], None, Unset]
        if isinstance(self.previous_time_plan, Unset):
            previous_time_plan = UNSET
        elif isinstance(self.previous_time_plan, TimePlan):
            previous_time_plan = self.previous_time_plan.to_dict()
        else:
            previous_time_plan = self.previous_time_plan

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "time_plan": time_plan,
                "note": note,
                "activities": activities,
                "target_inbox_tasks": target_inbox_tasks,
                "completed_nontarget_inbox_tasks": completed_nontarget_inbox_tasks,
                "sub_period_time_plans": sub_period_time_plans,
            }
        )
        if target_big_plans is not UNSET:
            field_dict["target_big_plans"] = target_big_plans
        if completed_nottarget_big_plans is not UNSET:
            field_dict["completed_nottarget_big_plans"] = completed_nottarget_big_plans
        if higher_time_plan is not UNSET:
            field_dict["higher_time_plan"] = higher_time_plan
        if previous_time_plan is not UNSET:
            field_dict["previous_time_plan"] = previous_time_plan

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.big_plan import BigPlan
        from ..models.inbox_task import InboxTask
        from ..models.note import Note
        from ..models.time_plan import TimePlan
        from ..models.time_plan_activity import TimePlanActivity

        d = src_dict.copy()
        time_plan = TimePlan.from_dict(d.pop("time_plan"))

        note = Note.from_dict(d.pop("note"))

        activities = []
        _activities = d.pop("activities")
        for activities_item_data in _activities:
            activities_item = TimePlanActivity.from_dict(activities_item_data)

            activities.append(activities_item)

        target_inbox_tasks = []
        _target_inbox_tasks = d.pop("target_inbox_tasks")
        for target_inbox_tasks_item_data in _target_inbox_tasks:
            target_inbox_tasks_item = InboxTask.from_dict(target_inbox_tasks_item_data)

            target_inbox_tasks.append(target_inbox_tasks_item)

        completed_nontarget_inbox_tasks = []
        _completed_nontarget_inbox_tasks = d.pop("completed_nontarget_inbox_tasks")
        for completed_nontarget_inbox_tasks_item_data in _completed_nontarget_inbox_tasks:
            completed_nontarget_inbox_tasks_item = InboxTask.from_dict(completed_nontarget_inbox_tasks_item_data)

            completed_nontarget_inbox_tasks.append(completed_nontarget_inbox_tasks_item)

        sub_period_time_plans = []
        _sub_period_time_plans = d.pop("sub_period_time_plans")
        for sub_period_time_plans_item_data in _sub_period_time_plans:
            sub_period_time_plans_item = TimePlan.from_dict(sub_period_time_plans_item_data)

            sub_period_time_plans.append(sub_period_time_plans_item)

        def _parse_target_big_plans(data: object) -> Union[List["BigPlan"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                target_big_plans_type_0 = []
                _target_big_plans_type_0 = data
                for target_big_plans_type_0_item_data in _target_big_plans_type_0:
                    target_big_plans_type_0_item = BigPlan.from_dict(target_big_plans_type_0_item_data)

                    target_big_plans_type_0.append(target_big_plans_type_0_item)

                return target_big_plans_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["BigPlan"], None, Unset], data)

        target_big_plans = _parse_target_big_plans(d.pop("target_big_plans", UNSET))

        def _parse_completed_nottarget_big_plans(data: object) -> Union[List["BigPlan"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                completed_nottarget_big_plans_type_0 = []
                _completed_nottarget_big_plans_type_0 = data
                for completed_nottarget_big_plans_type_0_item_data in _completed_nottarget_big_plans_type_0:
                    completed_nottarget_big_plans_type_0_item = BigPlan.from_dict(
                        completed_nottarget_big_plans_type_0_item_data
                    )

                    completed_nottarget_big_plans_type_0.append(completed_nottarget_big_plans_type_0_item)

                return completed_nottarget_big_plans_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["BigPlan"], None, Unset], data)

        completed_nottarget_big_plans = _parse_completed_nottarget_big_plans(
            d.pop("completed_nottarget_big_plans", UNSET)
        )

        def _parse_higher_time_plan(data: object) -> Union["TimePlan", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                higher_time_plan_type_0 = TimePlan.from_dict(data)

                return higher_time_plan_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TimePlan", None, Unset], data)

        higher_time_plan = _parse_higher_time_plan(d.pop("higher_time_plan", UNSET))

        def _parse_previous_time_plan(data: object) -> Union["TimePlan", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                previous_time_plan_type_0 = TimePlan.from_dict(data)

                return previous_time_plan_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TimePlan", None, Unset], data)

        previous_time_plan = _parse_previous_time_plan(d.pop("previous_time_plan", UNSET))

        time_plan_load_result = cls(
            time_plan=time_plan,
            note=note,
            activities=activities,
            target_inbox_tasks=target_inbox_tasks,
            completed_nontarget_inbox_tasks=completed_nontarget_inbox_tasks,
            sub_period_time_plans=sub_period_time_plans,
            target_big_plans=target_big_plans,
            completed_nottarget_big_plans=completed_nottarget_big_plans,
            higher_time_plan=higher_time_plan,
            previous_time_plan=previous_time_plan,
        )

        time_plan_load_result.additional_properties = d
        return time_plan_load_result

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