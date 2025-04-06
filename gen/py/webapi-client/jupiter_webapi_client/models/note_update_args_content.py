from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bulleted_list_block import BulletedListBlock
    from ..models.checklist_block import ChecklistBlock
    from ..models.code_block import CodeBlock
    from ..models.divider_block import DividerBlock
    from ..models.entity_reference_block import EntityReferenceBlock
    from ..models.heading_block import HeadingBlock
    from ..models.link_block import LinkBlock
    from ..models.numbered_list_block import NumberedListBlock
    from ..models.paragraph_block import ParagraphBlock
    from ..models.quote_block import QuoteBlock
    from ..models.table_block import TableBlock


T = TypeVar("T", bound="NoteUpdateArgsContent")


@_attrs_define
class NoteUpdateArgsContent:
    """
    Attributes:
        should_change (bool):
        value (Union[Unset, list[Union['BulletedListBlock', 'ChecklistBlock', 'CodeBlock', 'DividerBlock',
            'EntityReferenceBlock', 'HeadingBlock', 'LinkBlock', 'NumberedListBlock', 'ParagraphBlock', 'QuoteBlock',
            'TableBlock']]]):
    """

    should_change: bool
    value: Union[
        Unset,
        list[
            Union[
                "BulletedListBlock",
                "ChecklistBlock",
                "CodeBlock",
                "DividerBlock",
                "EntityReferenceBlock",
                "HeadingBlock",
                "LinkBlock",
                "NumberedListBlock",
                "ParagraphBlock",
                "QuoteBlock",
                "TableBlock",
            ]
        ],
    ] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.bulleted_list_block import BulletedListBlock
        from ..models.checklist_block import ChecklistBlock
        from ..models.code_block import CodeBlock
        from ..models.divider_block import DividerBlock
        from ..models.heading_block import HeadingBlock
        from ..models.link_block import LinkBlock
        from ..models.numbered_list_block import NumberedListBlock
        from ..models.paragraph_block import ParagraphBlock
        from ..models.quote_block import QuoteBlock
        from ..models.table_block import TableBlock

        should_change = self.should_change

        value: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.value, Unset):
            value = []
            for value_item_data in self.value:
                value_item: dict[str, Any]
                if isinstance(value_item_data, ParagraphBlock):
                    value_item = value_item_data.to_dict()
                elif isinstance(value_item_data, HeadingBlock):
                    value_item = value_item_data.to_dict()
                elif isinstance(value_item_data, BulletedListBlock):
                    value_item = value_item_data.to_dict()
                elif isinstance(value_item_data, NumberedListBlock):
                    value_item = value_item_data.to_dict()
                elif isinstance(value_item_data, ChecklistBlock):
                    value_item = value_item_data.to_dict()
                elif isinstance(value_item_data, TableBlock):
                    value_item = value_item_data.to_dict()
                elif isinstance(value_item_data, CodeBlock):
                    value_item = value_item_data.to_dict()
                elif isinstance(value_item_data, QuoteBlock):
                    value_item = value_item_data.to_dict()
                elif isinstance(value_item_data, DividerBlock):
                    value_item = value_item_data.to_dict()
                elif isinstance(value_item_data, LinkBlock):
                    value_item = value_item_data.to_dict()
                else:
                    value_item = value_item_data.to_dict()

                value.append(value_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "should_change": should_change,
            }
        )
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bulleted_list_block import BulletedListBlock
        from ..models.checklist_block import ChecklistBlock
        from ..models.code_block import CodeBlock
        from ..models.divider_block import DividerBlock
        from ..models.entity_reference_block import EntityReferenceBlock
        from ..models.heading_block import HeadingBlock
        from ..models.link_block import LinkBlock
        from ..models.numbered_list_block import NumberedListBlock
        from ..models.paragraph_block import ParagraphBlock
        from ..models.quote_block import QuoteBlock
        from ..models.table_block import TableBlock

        d = dict(src_dict)
        should_change = d.pop("should_change")

        value = []
        _value = d.pop("value", UNSET)
        for value_item_data in _value or []:

            def _parse_value_item(
                data: object,
            ) -> Union[
                "BulletedListBlock",
                "ChecklistBlock",
                "CodeBlock",
                "DividerBlock",
                "EntityReferenceBlock",
                "HeadingBlock",
                "LinkBlock",
                "NumberedListBlock",
                "ParagraphBlock",
                "QuoteBlock",
                "TableBlock",
            ]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    value_item_type_0 = ParagraphBlock.from_dict(data)

                    return value_item_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    value_item_type_1 = HeadingBlock.from_dict(data)

                    return value_item_type_1
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    value_item_type_2 = BulletedListBlock.from_dict(data)

                    return value_item_type_2
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    value_item_type_3 = NumberedListBlock.from_dict(data)

                    return value_item_type_3
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    value_item_type_4 = ChecklistBlock.from_dict(data)

                    return value_item_type_4
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    value_item_type_5 = TableBlock.from_dict(data)

                    return value_item_type_5
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    value_item_type_6 = CodeBlock.from_dict(data)

                    return value_item_type_6
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    value_item_type_7 = QuoteBlock.from_dict(data)

                    return value_item_type_7
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    value_item_type_8 = DividerBlock.from_dict(data)

                    return value_item_type_8
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    value_item_type_9 = LinkBlock.from_dict(data)

                    return value_item_type_9
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                value_item_type_10 = EntityReferenceBlock.from_dict(data)

                return value_item_type_10

            value_item = _parse_value_item(value_item_data)

            value.append(value_item)

        note_update_args_content = cls(
            should_change=should_change,
            value=value,
        )

        note_update_args_content.additional_properties = d
        return note_update_args_content

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
