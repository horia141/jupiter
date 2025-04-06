from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

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
        not_started (NestedResult): A result broken down by the various sources of inbox tasks.
        working (NestedResult): A result broken down by the various sources of inbox tasks.
        not_done (NestedResult): A result broken down by the various sources of inbox tasks.
        done (NestedResult): A result broken down by the various sources of inbox tasks.
    """

    created: "NestedResult"
    not_started: "NestedResult"
    working: "NestedResult"
    not_done: "NestedResult"
    done: "NestedResult"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created = self.created.to_dict()

        not_started = self.not_started.to_dict()

        working = self.working.to_dict()

        not_done = self.not_done.to_dict()

        done = self.done.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created": created,
                "not_started": not_started,
                "working": working,
                "not_done": not_done,
                "done": done,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.nested_result import NestedResult

        d = dict(src_dict)
        created = NestedResult.from_dict(d.pop("created"))

        not_started = NestedResult.from_dict(d.pop("not_started"))

        working = NestedResult.from_dict(d.pop("working"))

        not_done = NestedResult.from_dict(d.pop("not_done"))

        done = NestedResult.from_dict(d.pop("done"))

        inbox_tasks_summary = cls(
            created=created,
            not_started=not_started,
            working=working,
            not_done=not_done,
            done=done,
        )

        inbox_tasks_summary.additional_properties = d
        return inbox_tasks_summary

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
