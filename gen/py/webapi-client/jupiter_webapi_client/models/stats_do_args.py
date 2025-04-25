from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.sync_target import SyncTarget
from ..types import UNSET, Unset

T = TypeVar("T", bound="StatsDoArgs")


@_attrs_define
class StatsDoArgs:
    """StatsDoArgs.

    Attributes:
        today (Union[None, Unset, str]):
        stats_targets (Union[None, Unset, list[SyncTarget]]):
        filter_habit_ref_ids (Union[None, Unset, list[str]]):
        filter_big_plan_ref_ids (Union[None, Unset, list[str]]):
        filter_journal_ref_ids (Union[None, Unset, list[str]]):
    """

    today: Union[None, Unset, str] = UNSET
    stats_targets: Union[None, Unset, list[SyncTarget]] = UNSET
    filter_habit_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_big_plan_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_journal_ref_ids: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        today: Union[None, Unset, str]
        if isinstance(self.today, Unset):
            today = UNSET
        else:
            today = self.today

        stats_targets: Union[None, Unset, list[str]]
        if isinstance(self.stats_targets, Unset):
            stats_targets = UNSET
        elif isinstance(self.stats_targets, list):
            stats_targets = []
            for stats_targets_type_0_item_data in self.stats_targets:
                stats_targets_type_0_item = stats_targets_type_0_item_data.value
                stats_targets.append(stats_targets_type_0_item)

        else:
            stats_targets = self.stats_targets

        filter_habit_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_habit_ref_ids, Unset):
            filter_habit_ref_ids = UNSET
        elif isinstance(self.filter_habit_ref_ids, list):
            filter_habit_ref_ids = self.filter_habit_ref_ids

        else:
            filter_habit_ref_ids = self.filter_habit_ref_ids

        filter_big_plan_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_big_plan_ref_ids, Unset):
            filter_big_plan_ref_ids = UNSET
        elif isinstance(self.filter_big_plan_ref_ids, list):
            filter_big_plan_ref_ids = self.filter_big_plan_ref_ids

        else:
            filter_big_plan_ref_ids = self.filter_big_plan_ref_ids

        filter_journal_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_journal_ref_ids, Unset):
            filter_journal_ref_ids = UNSET
        elif isinstance(self.filter_journal_ref_ids, list):
            filter_journal_ref_ids = self.filter_journal_ref_ids

        else:
            filter_journal_ref_ids = self.filter_journal_ref_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if today is not UNSET:
            field_dict["today"] = today
        if stats_targets is not UNSET:
            field_dict["stats_targets"] = stats_targets
        if filter_habit_ref_ids is not UNSET:
            field_dict["filter_habit_ref_ids"] = filter_habit_ref_ids
        if filter_big_plan_ref_ids is not UNSET:
            field_dict["filter_big_plan_ref_ids"] = filter_big_plan_ref_ids
        if filter_journal_ref_ids is not UNSET:
            field_dict["filter_journal_ref_ids"] = filter_journal_ref_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_today(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        today = _parse_today(d.pop("today", UNSET))

        def _parse_stats_targets(data: object) -> Union[None, Unset, list[SyncTarget]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                stats_targets_type_0 = []
                _stats_targets_type_0 = data
                for stats_targets_type_0_item_data in _stats_targets_type_0:
                    stats_targets_type_0_item = SyncTarget(stats_targets_type_0_item_data)

                    stats_targets_type_0.append(stats_targets_type_0_item)

                return stats_targets_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[SyncTarget]], data)

        stats_targets = _parse_stats_targets(d.pop("stats_targets", UNSET))

        def _parse_filter_habit_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_habit_ref_ids_type_0 = cast(list[str], data)

                return filter_habit_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_habit_ref_ids = _parse_filter_habit_ref_ids(d.pop("filter_habit_ref_ids", UNSET))

        def _parse_filter_big_plan_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_big_plan_ref_ids_type_0 = cast(list[str], data)

                return filter_big_plan_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_big_plan_ref_ids = _parse_filter_big_plan_ref_ids(d.pop("filter_big_plan_ref_ids", UNSET))

        def _parse_filter_journal_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_journal_ref_ids_type_0 = cast(list[str], data)

                return filter_journal_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_journal_ref_ids = _parse_filter_journal_ref_ids(d.pop("filter_journal_ref_ids", UNSET))

        stats_do_args = cls(
            today=today,
            stats_targets=stats_targets,
            filter_habit_ref_ids=filter_habit_ref_ids,
            filter_big_plan_ref_ids=filter_big_plan_ref_ids,
            filter_journal_ref_ids=filter_journal_ref_ids,
        )

        stats_do_args.additional_properties = d
        return stats_do_args

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
