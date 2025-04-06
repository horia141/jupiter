from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

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


T = TypeVar("T", bound="DocCreateArgs")


@_attrs_define
class DocCreateArgs:
    """DocCreate args.

    Attributes:
        name (str): The doc name.
        content (list[Union['BulletedListBlock', 'ChecklistBlock', 'CodeBlock', 'DividerBlock', 'EntityReferenceBlock',
            'HeadingBlock', 'LinkBlock', 'NumberedListBlock', 'ParagraphBlock', 'QuoteBlock', 'TableBlock']]):
        parent_doc_ref_id (Union[None, Unset, str]):
    """

    name: str
    content: list[
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
    ]
    parent_doc_ref_id: Union[None, Unset, str] = UNSET
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

        name = self.name

        content = []
        for content_item_data in self.content:
            content_item: dict[str, Any]
            if isinstance(content_item_data, ParagraphBlock):
                content_item = content_item_data.to_dict()
            elif isinstance(content_item_data, HeadingBlock):
                content_item = content_item_data.to_dict()
            elif isinstance(content_item_data, BulletedListBlock):
                content_item = content_item_data.to_dict()
            elif isinstance(content_item_data, NumberedListBlock):
                content_item = content_item_data.to_dict()
            elif isinstance(content_item_data, ChecklistBlock):
                content_item = content_item_data.to_dict()
            elif isinstance(content_item_data, TableBlock):
                content_item = content_item_data.to_dict()
            elif isinstance(content_item_data, CodeBlock):
                content_item = content_item_data.to_dict()
            elif isinstance(content_item_data, QuoteBlock):
                content_item = content_item_data.to_dict()
            elif isinstance(content_item_data, DividerBlock):
                content_item = content_item_data.to_dict()
            elif isinstance(content_item_data, LinkBlock):
                content_item = content_item_data.to_dict()
            else:
                content_item = content_item_data.to_dict()

            content.append(content_item)

        parent_doc_ref_id: Union[None, Unset, str]
        if isinstance(self.parent_doc_ref_id, Unset):
            parent_doc_ref_id = UNSET
        else:
            parent_doc_ref_id = self.parent_doc_ref_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "content": content,
            }
        )
        if parent_doc_ref_id is not UNSET:
            field_dict["parent_doc_ref_id"] = parent_doc_ref_id

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
        name = d.pop("name")

        content = []
        _content = d.pop("content")
        for content_item_data in _content:

            def _parse_content_item(
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
                    content_item_type_0 = ParagraphBlock.from_dict(data)

                    return content_item_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    content_item_type_1 = HeadingBlock.from_dict(data)

                    return content_item_type_1
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    content_item_type_2 = BulletedListBlock.from_dict(data)

                    return content_item_type_2
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    content_item_type_3 = NumberedListBlock.from_dict(data)

                    return content_item_type_3
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    content_item_type_4 = ChecklistBlock.from_dict(data)

                    return content_item_type_4
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    content_item_type_5 = TableBlock.from_dict(data)

                    return content_item_type_5
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    content_item_type_6 = CodeBlock.from_dict(data)

                    return content_item_type_6
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    content_item_type_7 = QuoteBlock.from_dict(data)

                    return content_item_type_7
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    content_item_type_8 = DividerBlock.from_dict(data)

                    return content_item_type_8
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    content_item_type_9 = LinkBlock.from_dict(data)

                    return content_item_type_9
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                content_item_type_10 = EntityReferenceBlock.from_dict(data)

                return content_item_type_10

            content_item = _parse_content_item(content_item_data)

            content.append(content_item)

        def _parse_parent_doc_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        parent_doc_ref_id = _parse_parent_doc_ref_id(d.pop("parent_doc_ref_id", UNSET))

        doc_create_args = cls(
            name=name,
            content=content,
            parent_doc_ref_id=parent_doc_ref_id,
        )

        doc_create_args.additional_properties = d
        return doc_create_args

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
