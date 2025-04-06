from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.journal import Journal


T = TypeVar("T", bound="JournalLoadForDateAndPeriodResult")


@_attrs_define
class JournalLoadForDateAndPeriodResult:
    """Result.

    Attributes:
        sub_period_journals (list['Journal']):
        journal (Union['Journal', None, Unset]):
    """

    sub_period_journals: list["Journal"]
    journal: Union["Journal", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.journal import Journal

        sub_period_journals = []
        for sub_period_journals_item_data in self.sub_period_journals:
            sub_period_journals_item = sub_period_journals_item_data.to_dict()
            sub_period_journals.append(sub_period_journals_item)

        journal: Union[None, Unset, dict[str, Any]]
        if isinstance(self.journal, Unset):
            journal = UNSET
        elif isinstance(self.journal, Journal):
            journal = self.journal.to_dict()
        else:
            journal = self.journal

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sub_period_journals": sub_period_journals,
            }
        )
        if journal is not UNSET:
            field_dict["journal"] = journal

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.journal import Journal

        d = dict(src_dict)
        sub_period_journals = []
        _sub_period_journals = d.pop("sub_period_journals")
        for sub_period_journals_item_data in _sub_period_journals:
            sub_period_journals_item = Journal.from_dict(sub_period_journals_item_data)

            sub_period_journals.append(sub_period_journals_item)

        def _parse_journal(data: object) -> Union["Journal", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                journal_type_0 = Journal.from_dict(data)

                return journal_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Journal", None, Unset], data)

        journal = _parse_journal(d.pop("journal", UNSET))

        journal_load_for_date_and_period_result = cls(
            sub_period_journals=sub_period_journals,
            journal=journal,
        )

        journal_load_for_date_and_period_result.additional_properties = d
        return journal_load_for_date_and_period_result

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
