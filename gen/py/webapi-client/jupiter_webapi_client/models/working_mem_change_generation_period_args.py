from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod

T = TypeVar("T", bound="WorkingMemChangeGenerationPeriodArgs")


@_attrs_define
class WorkingMemChangeGenerationPeriodArgs:
    """WorkingMemChangeGenerationPeriodArgs.

    Attributes:
        generation_period (RecurringTaskPeriod): A period for a particular task.
    """

    generation_period: RecurringTaskPeriod
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        generation_period = self.generation_period.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "generation_period": generation_period,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        generation_period = RecurringTaskPeriod(d.pop("generation_period"))

        working_mem_change_generation_period_args = cls(
            generation_period=generation_period,
        )

        working_mem_change_generation_period_args.additional_properties = d
        return working_mem_change_generation_period_args

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
