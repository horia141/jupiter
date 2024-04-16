from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.person_update_args_birthday import PersonUpdateArgsBirthday
    from ..models.person_update_args_catch_up_actionable_from_day import PersonUpdateArgsCatchUpActionableFromDay
    from ..models.person_update_args_catch_up_actionable_from_month import PersonUpdateArgsCatchUpActionableFromMonth
    from ..models.person_update_args_catch_up_difficulty import PersonUpdateArgsCatchUpDifficulty
    from ..models.person_update_args_catch_up_due_at_day import PersonUpdateArgsCatchUpDueAtDay
    from ..models.person_update_args_catch_up_due_at_month import PersonUpdateArgsCatchUpDueAtMonth
    from ..models.person_update_args_catch_up_eisen import PersonUpdateArgsCatchUpEisen
    from ..models.person_update_args_catch_up_period import PersonUpdateArgsCatchUpPeriod
    from ..models.person_update_args_name import PersonUpdateArgsName
    from ..models.person_update_args_relationship import PersonUpdateArgsRelationship


T = TypeVar("T", bound="PersonUpdateArgs")


@_attrs_define
class PersonUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (PersonUpdateArgsName):
        relationship (PersonUpdateArgsRelationship):
        catch_up_period (PersonUpdateArgsCatchUpPeriod):
        catch_up_eisen (PersonUpdateArgsCatchUpEisen):
        catch_up_difficulty (PersonUpdateArgsCatchUpDifficulty):
        catch_up_actionable_from_day (PersonUpdateArgsCatchUpActionableFromDay):
        catch_up_actionable_from_month (PersonUpdateArgsCatchUpActionableFromMonth):
        catch_up_due_at_day (PersonUpdateArgsCatchUpDueAtDay):
        catch_up_due_at_month (PersonUpdateArgsCatchUpDueAtMonth):
        birthday (PersonUpdateArgsBirthday):
    """

    ref_id: str
    name: "PersonUpdateArgsName"
    relationship: "PersonUpdateArgsRelationship"
    catch_up_period: "PersonUpdateArgsCatchUpPeriod"
    catch_up_eisen: "PersonUpdateArgsCatchUpEisen"
    catch_up_difficulty: "PersonUpdateArgsCatchUpDifficulty"
    catch_up_actionable_from_day: "PersonUpdateArgsCatchUpActionableFromDay"
    catch_up_actionable_from_month: "PersonUpdateArgsCatchUpActionableFromMonth"
    catch_up_due_at_day: "PersonUpdateArgsCatchUpDueAtDay"
    catch_up_due_at_month: "PersonUpdateArgsCatchUpDueAtMonth"
    birthday: "PersonUpdateArgsBirthday"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        relationship = self.relationship.to_dict()

        catch_up_period = self.catch_up_period.to_dict()

        catch_up_eisen = self.catch_up_eisen.to_dict()

        catch_up_difficulty = self.catch_up_difficulty.to_dict()

        catch_up_actionable_from_day = self.catch_up_actionable_from_day.to_dict()

        catch_up_actionable_from_month = self.catch_up_actionable_from_month.to_dict()

        catch_up_due_at_day = self.catch_up_due_at_day.to_dict()

        catch_up_due_at_month = self.catch_up_due_at_month.to_dict()

        birthday = self.birthday.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "relationship": relationship,
                "catch_up_period": catch_up_period,
                "catch_up_eisen": catch_up_eisen,
                "catch_up_difficulty": catch_up_difficulty,
                "catch_up_actionable_from_day": catch_up_actionable_from_day,
                "catch_up_actionable_from_month": catch_up_actionable_from_month,
                "catch_up_due_at_day": catch_up_due_at_day,
                "catch_up_due_at_month": catch_up_due_at_month,
                "birthday": birthday,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.person_update_args_birthday import PersonUpdateArgsBirthday
        from ..models.person_update_args_catch_up_actionable_from_day import PersonUpdateArgsCatchUpActionableFromDay
        from ..models.person_update_args_catch_up_actionable_from_month import (
            PersonUpdateArgsCatchUpActionableFromMonth,
        )
        from ..models.person_update_args_catch_up_difficulty import PersonUpdateArgsCatchUpDifficulty
        from ..models.person_update_args_catch_up_due_at_day import PersonUpdateArgsCatchUpDueAtDay
        from ..models.person_update_args_catch_up_due_at_month import PersonUpdateArgsCatchUpDueAtMonth
        from ..models.person_update_args_catch_up_eisen import PersonUpdateArgsCatchUpEisen
        from ..models.person_update_args_catch_up_period import PersonUpdateArgsCatchUpPeriod
        from ..models.person_update_args_name import PersonUpdateArgsName
        from ..models.person_update_args_relationship import PersonUpdateArgsRelationship

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        name = PersonUpdateArgsName.from_dict(d.pop("name"))

        relationship = PersonUpdateArgsRelationship.from_dict(d.pop("relationship"))

        catch_up_period = PersonUpdateArgsCatchUpPeriod.from_dict(d.pop("catch_up_period"))

        catch_up_eisen = PersonUpdateArgsCatchUpEisen.from_dict(d.pop("catch_up_eisen"))

        catch_up_difficulty = PersonUpdateArgsCatchUpDifficulty.from_dict(d.pop("catch_up_difficulty"))

        catch_up_actionable_from_day = PersonUpdateArgsCatchUpActionableFromDay.from_dict(
            d.pop("catch_up_actionable_from_day")
        )

        catch_up_actionable_from_month = PersonUpdateArgsCatchUpActionableFromMonth.from_dict(
            d.pop("catch_up_actionable_from_month")
        )

        catch_up_due_at_day = PersonUpdateArgsCatchUpDueAtDay.from_dict(d.pop("catch_up_due_at_day"))

        catch_up_due_at_month = PersonUpdateArgsCatchUpDueAtMonth.from_dict(d.pop("catch_up_due_at_month"))

        birthday = PersonUpdateArgsBirthday.from_dict(d.pop("birthday"))

        person_update_args = cls(
            ref_id=ref_id,
            name=name,
            relationship=relationship,
            catch_up_period=catch_up_period,
            catch_up_eisen=catch_up_eisen,
            catch_up_difficulty=catch_up_difficulty,
            catch_up_actionable_from_day=catch_up_actionable_from_day,
            catch_up_actionable_from_month=catch_up_actionable_from_month,
            catch_up_due_at_day=catch_up_due_at_day,
            catch_up_due_at_month=catch_up_due_at_month,
            birthday=birthday,
        )

        person_update_args.additional_properties = d
        return person_update_args

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
