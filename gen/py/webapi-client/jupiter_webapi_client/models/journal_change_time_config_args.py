from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.journal_change_time_config_args_period import JournalChangeTimeConfigArgsPeriod
    from ..models.journal_change_time_config_args_right_now import JournalChangeTimeConfigArgsRightNow


T = TypeVar("T", bound="JournalChangeTimeConfigArgs")


@_attrs_define
class JournalChangeTimeConfigArgs:
    """Args.

    Attributes:
        ref_id (str): A generic entity id.
        right_now (JournalChangeTimeConfigArgsRightNow):
        period (JournalChangeTimeConfigArgsPeriod):
    """

    ref_id: str
    right_now: "JournalChangeTimeConfigArgsRightNow"
    period: "JournalChangeTimeConfigArgsPeriod"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        right_now = self.right_now.to_dict()

        period = self.period.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "right_now": right_now,
                "period": period,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.journal_change_time_config_args_period import JournalChangeTimeConfigArgsPeriod
        from ..models.journal_change_time_config_args_right_now import JournalChangeTimeConfigArgsRightNow

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        right_now = JournalChangeTimeConfigArgsRightNow.from_dict(d.pop("right_now"))

        period = JournalChangeTimeConfigArgsPeriod.from_dict(d.pop("period"))

        journal_change_time_config_args = cls(
            ref_id=ref_id,
            right_now=right_now,
            period=period,
        )

        journal_change_time_config_args.additional_properties = d
        return journal_change_time_config_args

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
