from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.code_block_kind import CodeBlockKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="CodeBlock")


@_attrs_define
class CodeBlock:
    """A code block.

    Attributes:
        correlation_id (str): A generic entity id.
        kind (CodeBlockKind):
        code (str):
        language (Union[None, Unset, str]):
        show_line_numbers (Union[None, Unset, bool]):
    """

    correlation_id: str
    kind: CodeBlockKind
    code: str
    language: Union[None, Unset, str] = UNSET
    show_line_numbers: Union[None, Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        correlation_id = self.correlation_id

        kind = self.kind.value

        code = self.code

        language: Union[None, Unset, str]
        if isinstance(self.language, Unset):
            language = UNSET
        else:
            language = self.language

        show_line_numbers: Union[None, Unset, bool]
        if isinstance(self.show_line_numbers, Unset):
            show_line_numbers = UNSET
        else:
            show_line_numbers = self.show_line_numbers

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "correlation_id": correlation_id,
                "kind": kind,
                "code": code,
            }
        )
        if language is not UNSET:
            field_dict["language"] = language
        if show_line_numbers is not UNSET:
            field_dict["show_line_numbers"] = show_line_numbers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        correlation_id = d.pop("correlation_id")

        kind = CodeBlockKind(d.pop("kind"))

        code = d.pop("code")

        def _parse_language(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        language = _parse_language(d.pop("language", UNSET))

        def _parse_show_line_numbers(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        show_line_numbers = _parse_show_line_numbers(d.pop("show_line_numbers", UNSET))

        code_block = cls(
            correlation_id=correlation_id,
            kind=kind,
            code=code,
            language=language,
            show_line_numbers=show_line_numbers,
        )

        code_block.additional_properties = d
        return code_block

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
