from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.difficulty import Difficulty
from ..models.eisen import Eisen
from ..models.metric_unit import MetricUnit
from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

T = TypeVar("T", bound="MetricCreateArgs")


@_attrs_define
class MetricCreateArgs:
    """PersonFindArgs.

    Attributes:
        name (str): THe metric name.
        icon (Union[Unset, str]): The icon for an entity.
        collection_period (Union[Unset, RecurringTaskPeriod]): A period for a particular task.
        collection_eisen (Union[Unset, Eisen]): The Eisenhower status of a particular task.
        collection_difficulty (Union[Unset, Difficulty]): The difficulty of a particular task.
        collection_actionable_from_day (Union[Unset, int]): The due day for a recurring task.
        collection_actionable_from_month (Union[Unset, int]): The due month for a recurring task.
        collection_due_at_day (Union[Unset, int]): The due day for a recurring task.
        collection_due_at_month (Union[Unset, int]): The due month for a recurring task.
        metric_unit (Union[Unset, MetricUnit]): The unit for a metric.
    """

    name: str
    icon: Union[Unset, str] = UNSET
    collection_period: Union[Unset, RecurringTaskPeriod] = UNSET
    collection_eisen: Union[Unset, Eisen] = UNSET
    collection_difficulty: Union[Unset, Difficulty] = UNSET
    collection_actionable_from_day: Union[Unset, int] = UNSET
    collection_actionable_from_month: Union[Unset, int] = UNSET
    collection_due_at_day: Union[Unset, int] = UNSET
    collection_due_at_month: Union[Unset, int] = UNSET
    metric_unit: Union[Unset, MetricUnit] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        icon = self.icon

        collection_period: Union[Unset, str] = UNSET
        if not isinstance(self.collection_period, Unset):
            collection_period = self.collection_period.value

        collection_eisen: Union[Unset, str] = UNSET
        if not isinstance(self.collection_eisen, Unset):
            collection_eisen = self.collection_eisen.value

        collection_difficulty: Union[Unset, str] = UNSET
        if not isinstance(self.collection_difficulty, Unset):
            collection_difficulty = self.collection_difficulty.value

        collection_actionable_from_day = self.collection_actionable_from_day

        collection_actionable_from_month = self.collection_actionable_from_month

        collection_due_at_day = self.collection_due_at_day

        collection_due_at_month = self.collection_due_at_month

        metric_unit: Union[Unset, str] = UNSET
        if not isinstance(self.metric_unit, Unset):
            metric_unit = self.metric_unit.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if icon is not UNSET:
            field_dict["icon"] = icon
        if collection_period is not UNSET:
            field_dict["collection_period"] = collection_period
        if collection_eisen is not UNSET:
            field_dict["collection_eisen"] = collection_eisen
        if collection_difficulty is not UNSET:
            field_dict["collection_difficulty"] = collection_difficulty
        if collection_actionable_from_day is not UNSET:
            field_dict["collection_actionable_from_day"] = collection_actionable_from_day
        if collection_actionable_from_month is not UNSET:
            field_dict["collection_actionable_from_month"] = collection_actionable_from_month
        if collection_due_at_day is not UNSET:
            field_dict["collection_due_at_day"] = collection_due_at_day
        if collection_due_at_month is not UNSET:
            field_dict["collection_due_at_month"] = collection_due_at_month
        if metric_unit is not UNSET:
            field_dict["metric_unit"] = metric_unit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        icon = d.pop("icon", UNSET)

        _collection_period = d.pop("collection_period", UNSET)
        collection_period: Union[Unset, RecurringTaskPeriod]
        if isinstance(_collection_period, Unset):
            collection_period = UNSET
        else:
            collection_period = RecurringTaskPeriod(_collection_period)

        _collection_eisen = d.pop("collection_eisen", UNSET)
        collection_eisen: Union[Unset, Eisen]
        if isinstance(_collection_eisen, Unset):
            collection_eisen = UNSET
        else:
            collection_eisen = Eisen(_collection_eisen)

        _collection_difficulty = d.pop("collection_difficulty", UNSET)
        collection_difficulty: Union[Unset, Difficulty]
        if isinstance(_collection_difficulty, Unset):
            collection_difficulty = UNSET
        else:
            collection_difficulty = Difficulty(_collection_difficulty)

        collection_actionable_from_day = d.pop("collection_actionable_from_day", UNSET)

        collection_actionable_from_month = d.pop("collection_actionable_from_month", UNSET)

        collection_due_at_day = d.pop("collection_due_at_day", UNSET)

        collection_due_at_month = d.pop("collection_due_at_month", UNSET)

        _metric_unit = d.pop("metric_unit", UNSET)
        metric_unit: Union[Unset, MetricUnit]
        if isinstance(_metric_unit, Unset):
            metric_unit = UNSET
        else:
            metric_unit = MetricUnit(_metric_unit)

        metric_create_args = cls(
            name=name,
            icon=icon,
            collection_period=collection_period,
            collection_eisen=collection_eisen,
            collection_difficulty=collection_difficulty,
            collection_actionable_from_day=collection_actionable_from_day,
            collection_actionable_from_month=collection_actionable_from_month,
            collection_due_at_day=collection_due_at_day,
            collection_due_at_month=collection_due_at_month,
            metric_unit=metric_unit,
        )

        metric_create_args.additional_properties = d
        return metric_create_args

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
