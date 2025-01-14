from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.nested_result import NestedResult


T = TypeVar("T", bound="InboxTasksSummary")


@_attrs_define
class InboxTasksSummary:
    """A bigger summary for inbox tasks.

    Attributes:
        created (NestedResult): A result broken down by the various sources of inbox tasks.
        accepted (NestedResult): A result broken down by the various sources of inbox tasks.
        working (NestedResult): A result broken down by the various sources of inbox tasks.
        not_done (NestedResult): A result broken down by the various sources of inbox tasks.
        done (NestedResult): A result broken down by the various sources of inbox tasks.
    """

    created: "NestedResult"
    accepted: "NestedResult"
    working: "NestedResult"
    not_done: "NestedResult"
    done: "NestedResult"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created = self.created.to_dict()

        accepted = self.accepted.to_dict()

        working = self.working.to_dict()

        not_done = self.not_done.to_dict()

        done = self.done.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created": created,
                "accepted": accepted,
                "working": working,
                "not_done": not_done,
                "done": done,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.nested_result import NestedResult

        d = src_dict.copy()
        created = NestedResult.from_dict(d.pop("created"))

        accepted = NestedResult.from_dict(d.pop("accepted"))

        working = NestedResult.from_dict(d.pop("working"))

        not_done = NestedResult.from_dict(d.pop("not_done"))

        done = NestedResult.from_dict(d.pop("done"))

        inbox_tasks_summary = cls(
            created=created,
            accepted=accepted,
            working=working,
            not_done=not_done,
            done=done,
        )

        inbox_tasks_summary.additional_properties = d
        return inbox_tasks_summary

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
