from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.home_tab_target import HomeTabTarget
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.big_screen_home_tab_widget_placement import BigScreenHomeTabWidgetPlacement
    from ..models.small_screen_home_tab_widget_placement import SmallScreenHomeTabWidgetPlacement


T = TypeVar("T", bound="HomeTab")


@_attrs_define
class HomeTab:
    """A tab on the home page.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name for an entity which acts as both name and unique identifier.
        home_config_ref_id (str):
        target (HomeTabTarget): A target for a tab.
        widget_placement (Union['BigScreenHomeTabWidgetPlacement', 'SmallScreenHomeTabWidgetPlacement']):
        archival_reason (Union[None, Unset, str]):
        archived_time (Union[None, Unset, str]):
        icon (Union[None, Unset, str]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    home_config_ref_id: str
    target: HomeTabTarget
    widget_placement: Union["BigScreenHomeTabWidgetPlacement", "SmallScreenHomeTabWidgetPlacement"]
    archival_reason: Union[None, Unset, str] = UNSET
    archived_time: Union[None, Unset, str] = UNSET
    icon: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.big_screen_home_tab_widget_placement import BigScreenHomeTabWidgetPlacement

        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        home_config_ref_id = self.home_config_ref_id

        target = self.target.value

        widget_placement: dict[str, Any]
        if isinstance(self.widget_placement, BigScreenHomeTabWidgetPlacement):
            widget_placement = self.widget_placement.to_dict()
        else:
            widget_placement = self.widget_placement.to_dict()

        archival_reason: Union[None, Unset, str]
        if isinstance(self.archival_reason, Unset):
            archival_reason = UNSET
        else:
            archival_reason = self.archival_reason

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        icon: Union[None, Unset, str]
        if isinstance(self.icon, Unset):
            icon = UNSET
        else:
            icon = self.icon

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "home_config_ref_id": home_config_ref_id,
                "target": target,
                "widget_placement": widget_placement,
            }
        )
        if archival_reason is not UNSET:
            field_dict["archival_reason"] = archival_reason
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if icon is not UNSET:
            field_dict["icon"] = icon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.big_screen_home_tab_widget_placement import BigScreenHomeTabWidgetPlacement
        from ..models.small_screen_home_tab_widget_placement import SmallScreenHomeTabWidgetPlacement

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        home_config_ref_id = d.pop("home_config_ref_id")

        target = HomeTabTarget(d.pop("target"))

        def _parse_widget_placement(
            data: object,
        ) -> Union["BigScreenHomeTabWidgetPlacement", "SmallScreenHomeTabWidgetPlacement"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                widget_placement_type_0 = BigScreenHomeTabWidgetPlacement.from_dict(data)

                return widget_placement_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            widget_placement_type_1 = SmallScreenHomeTabWidgetPlacement.from_dict(data)

            return widget_placement_type_1

        widget_placement = _parse_widget_placement(d.pop("widget_placement"))

        def _parse_archival_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archival_reason = _parse_archival_reason(d.pop("archival_reason", UNSET))

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_icon(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        icon = _parse_icon(d.pop("icon", UNSET))

        home_tab = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            home_config_ref_id=home_config_ref_id,
            target=target,
            widget_placement=widget_placement,
            archival_reason=archival_reason,
            archived_time=archived_time,
            icon=icon,
        )

        home_tab.additional_properties = d
        return home_tab

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
