from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.metric_update_args_collection_actionable_from_day import MetricUpdateArgsCollectionActionableFromDay
    from ..models.metric_update_args_collection_actionable_from_month import (
        MetricUpdateArgsCollectionActionableFromMonth,
    )
    from ..models.metric_update_args_collection_difficulty import MetricUpdateArgsCollectionDifficulty
    from ..models.metric_update_args_collection_due_at_day import MetricUpdateArgsCollectionDueAtDay
    from ..models.metric_update_args_collection_due_at_month import MetricUpdateArgsCollectionDueAtMonth
    from ..models.metric_update_args_collection_eisen import MetricUpdateArgsCollectionEisen
    from ..models.metric_update_args_collection_period import MetricUpdateArgsCollectionPeriod
    from ..models.metric_update_args_icon import MetricUpdateArgsIcon
    from ..models.metric_update_args_name import MetricUpdateArgsName


T = TypeVar("T", bound="MetricUpdateArgs")


@_attrs_define
class MetricUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (MetricUpdateArgsName):
        icon (MetricUpdateArgsIcon):
        collection_period (MetricUpdateArgsCollectionPeriod):
        collection_eisen (MetricUpdateArgsCollectionEisen):
        collection_difficulty (MetricUpdateArgsCollectionDifficulty):
        collection_actionable_from_day (MetricUpdateArgsCollectionActionableFromDay):
        collection_actionable_from_month (MetricUpdateArgsCollectionActionableFromMonth):
        collection_due_at_day (MetricUpdateArgsCollectionDueAtDay):
        collection_due_at_month (MetricUpdateArgsCollectionDueAtMonth):
    """

    ref_id: str
    name: "MetricUpdateArgsName"
    icon: "MetricUpdateArgsIcon"
    collection_period: "MetricUpdateArgsCollectionPeriod"
    collection_eisen: "MetricUpdateArgsCollectionEisen"
    collection_difficulty: "MetricUpdateArgsCollectionDifficulty"
    collection_actionable_from_day: "MetricUpdateArgsCollectionActionableFromDay"
    collection_actionable_from_month: "MetricUpdateArgsCollectionActionableFromMonth"
    collection_due_at_day: "MetricUpdateArgsCollectionDueAtDay"
    collection_due_at_month: "MetricUpdateArgsCollectionDueAtMonth"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        icon = self.icon.to_dict()

        collection_period = self.collection_period.to_dict()

        collection_eisen = self.collection_eisen.to_dict()

        collection_difficulty = self.collection_difficulty.to_dict()

        collection_actionable_from_day = self.collection_actionable_from_day.to_dict()

        collection_actionable_from_month = self.collection_actionable_from_month.to_dict()

        collection_due_at_day = self.collection_due_at_day.to_dict()

        collection_due_at_month = self.collection_due_at_month.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "icon": icon,
                "collection_period": collection_period,
                "collection_eisen": collection_eisen,
                "collection_difficulty": collection_difficulty,
                "collection_actionable_from_day": collection_actionable_from_day,
                "collection_actionable_from_month": collection_actionable_from_month,
                "collection_due_at_day": collection_due_at_day,
                "collection_due_at_month": collection_due_at_month,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.metric_update_args_collection_actionable_from_day import (
            MetricUpdateArgsCollectionActionableFromDay,
        )
        from ..models.metric_update_args_collection_actionable_from_month import (
            MetricUpdateArgsCollectionActionableFromMonth,
        )
        from ..models.metric_update_args_collection_difficulty import MetricUpdateArgsCollectionDifficulty
        from ..models.metric_update_args_collection_due_at_day import MetricUpdateArgsCollectionDueAtDay
        from ..models.metric_update_args_collection_due_at_month import MetricUpdateArgsCollectionDueAtMonth
        from ..models.metric_update_args_collection_eisen import MetricUpdateArgsCollectionEisen
        from ..models.metric_update_args_collection_period import MetricUpdateArgsCollectionPeriod
        from ..models.metric_update_args_icon import MetricUpdateArgsIcon
        from ..models.metric_update_args_name import MetricUpdateArgsName

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = MetricUpdateArgsName.from_dict(d.pop("name"))

        icon = MetricUpdateArgsIcon.from_dict(d.pop("icon"))

        collection_period = MetricUpdateArgsCollectionPeriod.from_dict(d.pop("collection_period"))

        collection_eisen = MetricUpdateArgsCollectionEisen.from_dict(d.pop("collection_eisen"))

        collection_difficulty = MetricUpdateArgsCollectionDifficulty.from_dict(d.pop("collection_difficulty"))

        collection_actionable_from_day = MetricUpdateArgsCollectionActionableFromDay.from_dict(
            d.pop("collection_actionable_from_day")
        )

        collection_actionable_from_month = MetricUpdateArgsCollectionActionableFromMonth.from_dict(
            d.pop("collection_actionable_from_month")
        )

        collection_due_at_day = MetricUpdateArgsCollectionDueAtDay.from_dict(d.pop("collection_due_at_day"))

        collection_due_at_month = MetricUpdateArgsCollectionDueAtMonth.from_dict(d.pop("collection_due_at_month"))

        metric_update_args = cls(
            ref_id=ref_id,
            name=name,
            icon=icon,
            collection_period=collection_period,
            collection_eisen=collection_eisen,
            collection_difficulty=collection_difficulty,
            collection_actionable_from_day=collection_actionable_from_day,
            collection_actionable_from_month=collection_actionable_from_month,
            collection_due_at_day=collection_due_at_day,
            collection_due_at_month=collection_due_at_month,
        )

        metric_update_args.additional_properties = d
        return metric_update_args

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
