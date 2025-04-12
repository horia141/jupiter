from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.habit_repeats_strategy import HabitRepeatsStrategy
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.recurring_task_gen_params import RecurringTaskGenParams


T = TypeVar("T", bound="Habit")


@_attrs_define
class Habit:
    """A habit.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The habit name.
        habit_collection_ref_id (str):
        project_ref_id (str): A generic entity id.
        gen_params (RecurringTaskGenParams): Parameters for metric collection.
        suspended (bool):
        archival_reason (Union[None, Unset, str]):
        archived_time (Union[None, Unset, str]):
        repeats_strategy (Union[HabitRepeatsStrategy, None, Unset]):
        repeats_in_period_count (Union[None, Unset, int]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    habit_collection_ref_id: str
    project_ref_id: str
    gen_params: "RecurringTaskGenParams"
    suspended: bool
    archival_reason: Union[None, Unset, str] = UNSET
    archived_time: Union[None, Unset, str] = UNSET
    repeats_strategy: Union[HabitRepeatsStrategy, None, Unset] = UNSET
    repeats_in_period_count: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        habit_collection_ref_id = self.habit_collection_ref_id

        project_ref_id = self.project_ref_id

        gen_params = self.gen_params.to_dict()

        suspended = self.suspended

        archival_reason: Union[None, Unset, str]
        if isinstance(self.archival_reason, Unset):
            archival_reason = UNSET
        else:
            archival_reason = self.archival_reason

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        repeats_strategy: Union[None, Unset, str]
        if isinstance(self.repeats_strategy, Unset):
            repeats_strategy = UNSET
        elif isinstance(self.repeats_strategy, HabitRepeatsStrategy):
            repeats_strategy = self.repeats_strategy.value
        else:
            repeats_strategy = self.repeats_strategy

        repeats_in_period_count: Union[None, Unset, int]
        if isinstance(self.repeats_in_period_count, Unset):
            repeats_in_period_count = UNSET
        else:
            repeats_in_period_count = self.repeats_in_period_count

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
                "habit_collection_ref_id": habit_collection_ref_id,
                "project_ref_id": project_ref_id,
                "gen_params": gen_params,
                "suspended": suspended,
            }
        )
        if archival_reason is not UNSET:
            field_dict["archival_reason"] = archival_reason
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if repeats_strategy is not UNSET:
            field_dict["repeats_strategy"] = repeats_strategy
        if repeats_in_period_count is not UNSET:
            field_dict["repeats_in_period_count"] = repeats_in_period_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.recurring_task_gen_params import RecurringTaskGenParams

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        habit_collection_ref_id = d.pop("habit_collection_ref_id")

        project_ref_id = d.pop("project_ref_id")

        gen_params = RecurringTaskGenParams.from_dict(d.pop("gen_params"))

        suspended = d.pop("suspended")

        def _parse_archival_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archival_reason = _parse_archival_reason(d.pop("archival_reason", UNSET))

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_repeats_strategy(data: object) -> Union[HabitRepeatsStrategy, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                repeats_strategy_type_0 = HabitRepeatsStrategy(data)

                return repeats_strategy_type_0
            except:  # noqa: E722
                pass
            return cast(Union[HabitRepeatsStrategy, None, Unset], data)

        repeats_strategy = _parse_repeats_strategy(d.pop("repeats_strategy", UNSET))

        def _parse_repeats_in_period_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        repeats_in_period_count = _parse_repeats_in_period_count(d.pop("repeats_in_period_count", UNSET))

        habit = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            habit_collection_ref_id=habit_collection_ref_id,
            project_ref_id=project_ref_id,
            gen_params=gen_params,
            suspended=suspended,
            archival_reason=archival_reason,
            archived_time=archived_time,
            repeats_strategy=repeats_strategy,
            repeats_in_period_count=repeats_in_period_count,
        )

        habit.additional_properties = d
        return habit

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
