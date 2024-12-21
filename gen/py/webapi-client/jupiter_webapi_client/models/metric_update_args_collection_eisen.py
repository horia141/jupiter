from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.eisen import Eisen
from ..types import UNSET, Unset

T = TypeVar("T", bound="MetricUpdateArgsCollectionEisen")


@_attrs_define
class MetricUpdateArgsCollectionEisen:
    """
    Attributes:
        should_change (bool):
        value (Union[Eisen, None, Unset]):
    """

    should_change: bool
    value: Union[Eisen, None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        should_change = self.should_change

        value: Union[None, Unset, str]
        if isinstance(self.value, Unset):
            value = UNSET
        elif isinstance(self.value, Eisen):
            value = self.value.value
        else:
            value = self.value

        field_dict: Dict[str, Any] = {}
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
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        should_change = d.pop("should_change")

        def _parse_value(data: object) -> Union[Eisen, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                value_type_0 = Eisen(data)

                return value_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Eisen, None, Unset], data)

        value = _parse_value(d.pop("value", UNSET))

        metric_update_args_collection_eisen = cls(
            should_change=should_change,
            value=value,
        )

        metric_update_args_collection_eisen.additional_properties = d
        return metric_update_args_collection_eisen

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
