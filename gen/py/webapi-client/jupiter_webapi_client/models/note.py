from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.note_domain import NoteDomain
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


T = TypeVar("T", bound="Note")


@_attrs_define
class Note:
    """A note in the notebook.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name for an entity which acts as both name and unique identifier.
        note_collection (str):
        domain (NoteDomain): The source of a note.
        source_entity_ref_id (str): A generic entity id.
        content (List[Union['BulletedListBlock', 'ChecklistBlock', 'CodeBlock', 'DividerBlock', 'EntityReferenceBlock',
            'HeadingBlock', 'LinkBlock', 'NumberedListBlock', 'ParagraphBlock', 'QuoteBlock', 'TableBlock']]):
        archived_time (Union[Unset, str]): A timestamp in the application.
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    note_collection: str
    domain: NoteDomain
    source_entity_ref_id: str
    content: List[
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
    archived_time: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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

        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        note_collection = self.note_collection

        domain = self.domain.value

        source_entity_ref_id = self.source_entity_ref_id

        content = []
        for content_item_data in self.content:
            content_item: Dict[str, Any]
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

        archived_time = self.archived_time

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "note_collection": note_collection,
                "domain": domain,
                "source_entity_ref_id": source_entity_ref_id,
                "content": content,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
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

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        note_collection = d.pop("note_collection")

        domain = NoteDomain(d.pop("domain"))

        source_entity_ref_id = d.pop("source_entity_ref_id")

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

        archived_time = d.pop("archived_time", UNSET)

        note = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            note_collection=note_collection,
            domain=domain,
            source_entity_ref_id=source_entity_ref_id,
            content=content,
            archived_time=archived_time,
        )

        note.additional_properties = d
        return note

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
