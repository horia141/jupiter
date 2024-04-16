from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.project import Project


T = TypeVar("T", bound="PersonLoadSettingsResult")


@_attrs_define
class PersonLoadSettingsResult:
    """PersonLoadSettings results.

    Attributes:
        catch_up_project (Project): The project.
    """

    catch_up_project: "Project"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        catch_up_project = self.catch_up_project.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "catch_up_project": catch_up_project,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.project import Project

        d = src_dict.copy()
        catch_up_project = Project.from_dict(d.pop("catch_up_project"))

        person_load_settings_result = cls(
            catch_up_project=catch_up_project,
        )

        person_load_settings_result.additional_properties = d
        return person_load_settings_result

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
