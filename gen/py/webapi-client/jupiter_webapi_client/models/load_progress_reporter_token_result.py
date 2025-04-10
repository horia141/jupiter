from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="LoadProgressReporterTokenResult")


@_attrs_define
class LoadProgressReporterTokenResult:
    """Get progress reporter token result.

    Attributes:
        progress_reporter_token_ext (str): An externally facing authentication token.
    """

    progress_reporter_token_ext: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        progress_reporter_token_ext = self.progress_reporter_token_ext

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "progress_reporter_token_ext": progress_reporter_token_ext,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        progress_reporter_token_ext = d.pop("progress_reporter_token_ext")

        load_progress_reporter_token_result = cls(
            progress_reporter_token_ext=progress_reporter_token_ext,
        )

        load_progress_reporter_token_result.additional_properties = d
        return load_progress_reporter_token_result

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
