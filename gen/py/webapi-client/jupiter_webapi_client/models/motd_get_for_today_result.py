from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.motd import MOTD


T = TypeVar("T", bound="MOTDGetForTodayResult")


@_attrs_define
class MOTDGetForTodayResult:
    """Result for getting a MOTD.

    Attributes:
        motd (MOTD): A Message of the Day.
    """

    motd: "MOTD"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        motd = self.motd.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "motd": motd,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.motd import MOTD

        d = dict(src_dict)
        motd = MOTD.from_dict(d.pop("motd"))

        motd_get_for_today_result = cls(
            motd=motd,
        )

        motd_get_for_today_result.additional_properties = d
        return motd_get_for_today_result

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
