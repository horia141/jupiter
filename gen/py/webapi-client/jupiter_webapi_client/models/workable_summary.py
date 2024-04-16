from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.workable_big_plan import WorkableBigPlan


T = TypeVar("T", bound="WorkableSummary")


@_attrs_define
class WorkableSummary:
    """The reporting summary.

    Attributes:
        created_cnt (int):
        accepted_cnt (int):
        working_cnt (int):
        not_done_cnt (int):
        done_cnt (int):
        not_done_big_plans (List['WorkableBigPlan']):
        done_big_plans (List['WorkableBigPlan']):
    """

    created_cnt: int
    accepted_cnt: int
    working_cnt: int
    not_done_cnt: int
    done_cnt: int
    not_done_big_plans: List["WorkableBigPlan"]
    done_big_plans: List["WorkableBigPlan"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_cnt = self.created_cnt

        accepted_cnt = self.accepted_cnt

        working_cnt = self.working_cnt

        not_done_cnt = self.not_done_cnt

        done_cnt = self.done_cnt

        not_done_big_plans = []
        for not_done_big_plans_item_data in self.not_done_big_plans:
            not_done_big_plans_item = not_done_big_plans_item_data.to_dict()
            not_done_big_plans.append(not_done_big_plans_item)

        done_big_plans = []
        for done_big_plans_item_data in self.done_big_plans:
            done_big_plans_item = done_big_plans_item_data.to_dict()
            done_big_plans.append(done_big_plans_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_cnt": created_cnt,
                "accepted_cnt": accepted_cnt,
                "working_cnt": working_cnt,
                "not_done_cnt": not_done_cnt,
                "done_cnt": done_cnt,
                "not_done_big_plans": not_done_big_plans,
                "done_big_plans": done_big_plans,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.workable_big_plan import WorkableBigPlan

        d = src_dict.copy()
        created_cnt = d.pop("created_cnt")

        accepted_cnt = d.pop("accepted_cnt")

        working_cnt = d.pop("working_cnt")

        not_done_cnt = d.pop("not_done_cnt")

        done_cnt = d.pop("done_cnt")

        not_done_big_plans = []
        _not_done_big_plans = d.pop("not_done_big_plans")
        for not_done_big_plans_item_data in _not_done_big_plans:
            not_done_big_plans_item = WorkableBigPlan.from_dict(not_done_big_plans_item_data)

            not_done_big_plans.append(not_done_big_plans_item)

        done_big_plans = []
        _done_big_plans = d.pop("done_big_plans")
        for done_big_plans_item_data in _done_big_plans:
            done_big_plans_item = WorkableBigPlan.from_dict(done_big_plans_item_data)

            done_big_plans.append(done_big_plans_item)

        workable_summary = cls(
            created_cnt=created_cnt,
            accepted_cnt=accepted_cnt,
            working_cnt=working_cnt,
            not_done_cnt=not_done_cnt,
            done_cnt=done_cnt,
            not_done_big_plans=not_done_big_plans,
            done_big_plans=done_big_plans,
        )

        workable_summary.additional_properties = d
        return workable_summary

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
