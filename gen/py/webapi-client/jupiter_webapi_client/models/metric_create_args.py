from typing import Any, Dict, List, Type, TypeVar, Union, cast

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
        icon (Union[None, Unset, str]):
        collection_period (Union[None, RecurringTaskPeriod, Unset]):
        collection_eisen (Union[Eisen, None, Unset]):
        collection_difficulty (Union[Difficulty, None, Unset]):
        collection_actionable_from_day (Union[None, Unset, int]):
        collection_actionable_from_month (Union[None, Unset, int]):
        collection_due_at_day (Union[None, Unset, int]):
        collection_due_at_month (Union[None, Unset, int]):
        metric_unit (Union[MetricUnit, None, Unset]):
    """

    name: str
    icon: Union[None, Unset, str] = UNSET
    collection_period: Union[None, RecurringTaskPeriod, Unset] = UNSET
    collection_eisen: Union[Eisen, None, Unset] = UNSET
    collection_difficulty: Union[Difficulty, None, Unset] = UNSET
    collection_actionable_from_day: Union[None, Unset, int] = UNSET
    collection_actionable_from_month: Union[None, Unset, int] = UNSET
    collection_due_at_day: Union[None, Unset, int] = UNSET
    collection_due_at_month: Union[None, Unset, int] = UNSET
    metric_unit: Union[MetricUnit, None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        icon: Union[None, Unset, str]
        if isinstance(self.icon, Unset):
            icon = UNSET
        else:
            icon = self.icon

        collection_period: Union[None, Unset, str]
        if isinstance(self.collection_period, Unset):
            collection_period = UNSET
        elif isinstance(self.collection_period, RecurringTaskPeriod):
            collection_period = self.collection_period.value
        else:
            collection_period = self.collection_period

        collection_eisen: Union[None, Unset, str]
        if isinstance(self.collection_eisen, Unset):
            collection_eisen = UNSET
        elif isinstance(self.collection_eisen, Eisen):
            collection_eisen = self.collection_eisen.value
        else:
            collection_eisen = self.collection_eisen

        collection_difficulty: Union[None, Unset, str]
        if isinstance(self.collection_difficulty, Unset):
            collection_difficulty = UNSET
        elif isinstance(self.collection_difficulty, Difficulty):
            collection_difficulty = self.collection_difficulty.value
        else:
            collection_difficulty = self.collection_difficulty

        collection_actionable_from_day: Union[None, Unset, int]
        if isinstance(self.collection_actionable_from_day, Unset):
            collection_actionable_from_day = UNSET
        else:
            collection_actionable_from_day = self.collection_actionable_from_day

        collection_actionable_from_month: Union[None, Unset, int]
        if isinstance(self.collection_actionable_from_month, Unset):
            collection_actionable_from_month = UNSET
        else:
            collection_actionable_from_month = self.collection_actionable_from_month

        collection_due_at_day: Union[None, Unset, int]
        if isinstance(self.collection_due_at_day, Unset):
            collection_due_at_day = UNSET
        else:
            collection_due_at_day = self.collection_due_at_day

        collection_due_at_month: Union[None, Unset, int]
        if isinstance(self.collection_due_at_month, Unset):
            collection_due_at_month = UNSET
        else:
            collection_due_at_month = self.collection_due_at_month

        metric_unit: Union[None, Unset, str]
        if isinstance(self.metric_unit, Unset):
            metric_unit = UNSET
        elif isinstance(self.metric_unit, MetricUnit):
            metric_unit = self.metric_unit.value
        else:
            metric_unit = self.metric_unit

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

        def _parse_icon(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        icon = _parse_icon(d.pop("icon", UNSET))

        def _parse_collection_period(data: object) -> Union[None, RecurringTaskPeriod, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                collection_period_type_0 = RecurringTaskPeriod(data)

                return collection_period_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, RecurringTaskPeriod, Unset], data)

        collection_period = _parse_collection_period(d.pop("collection_period", UNSET))

        def _parse_collection_eisen(data: object) -> Union[Eisen, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                collection_eisen_type_0 = Eisen(data)

                return collection_eisen_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Eisen, None, Unset], data)

        collection_eisen = _parse_collection_eisen(d.pop("collection_eisen", UNSET))

        def _parse_collection_difficulty(data: object) -> Union[Difficulty, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                collection_difficulty_type_0 = Difficulty(data)

                return collection_difficulty_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Difficulty, None, Unset], data)

        collection_difficulty = _parse_collection_difficulty(d.pop("collection_difficulty", UNSET))

        def _parse_collection_actionable_from_day(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        collection_actionable_from_day = _parse_collection_actionable_from_day(
            d.pop("collection_actionable_from_day", UNSET)
        )

        def _parse_collection_actionable_from_month(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        collection_actionable_from_month = _parse_collection_actionable_from_month(
            d.pop("collection_actionable_from_month", UNSET)
        )

        def _parse_collection_due_at_day(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        collection_due_at_day = _parse_collection_due_at_day(d.pop("collection_due_at_day", UNSET))

        def _parse_collection_due_at_month(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        collection_due_at_month = _parse_collection_due_at_month(d.pop("collection_due_at_month", UNSET))

        def _parse_metric_unit(data: object) -> Union[MetricUnit, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                metric_unit_type_0 = MetricUnit(data)

                return metric_unit_type_0
            except:  # noqa: E722
                pass
            return cast(Union[MetricUnit, None, Unset], data)

        metric_unit = _parse_metric_unit(d.pop("metric_unit", UNSET))

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
