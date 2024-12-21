from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.difficulty import Difficulty
from ..models.eisen import Eisen
from ..models.person_relationship import PersonRelationship
from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

T = TypeVar("T", bound="PersonCreateArgs")


@_attrs_define
class PersonCreateArgs:
    """Person create args..

    Attributes:
        name (str): The person name.
        relationship (PersonRelationship): The relationship the user has with a person.
        catch_up_period (Union[None, RecurringTaskPeriod, Unset]):
        catch_up_eisen (Union[Eisen, None, Unset]):
        catch_up_difficulty (Union[Difficulty, None, Unset]):
        catch_up_actionable_from_day (Union[None, Unset, int]):
        catch_up_actionable_from_month (Union[None, Unset, int]):
        catch_up_due_at_day (Union[None, Unset, int]):
        catch_up_due_at_month (Union[None, Unset, int]):
        birthday (Union[None, Unset, str]):
    """

    name: str
    relationship: PersonRelationship
    catch_up_period: Union[None, RecurringTaskPeriod, Unset] = UNSET
    catch_up_eisen: Union[Eisen, None, Unset] = UNSET
    catch_up_difficulty: Union[Difficulty, None, Unset] = UNSET
    catch_up_actionable_from_day: Union[None, Unset, int] = UNSET
    catch_up_actionable_from_month: Union[None, Unset, int] = UNSET
    catch_up_due_at_day: Union[None, Unset, int] = UNSET
    catch_up_due_at_month: Union[None, Unset, int] = UNSET
    birthday: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        relationship = self.relationship.value

        catch_up_period: Union[None, Unset, str]
        if isinstance(self.catch_up_period, Unset):
            catch_up_period = UNSET
        elif isinstance(self.catch_up_period, RecurringTaskPeriod):
            catch_up_period = self.catch_up_period.value
        else:
            catch_up_period = self.catch_up_period

        catch_up_eisen: Union[None, Unset, str]
        if isinstance(self.catch_up_eisen, Unset):
            catch_up_eisen = UNSET
        elif isinstance(self.catch_up_eisen, Eisen):
            catch_up_eisen = self.catch_up_eisen.value
        else:
            catch_up_eisen = self.catch_up_eisen

        catch_up_difficulty: Union[None, Unset, str]
        if isinstance(self.catch_up_difficulty, Unset):
            catch_up_difficulty = UNSET
        elif isinstance(self.catch_up_difficulty, Difficulty):
            catch_up_difficulty = self.catch_up_difficulty.value
        else:
            catch_up_difficulty = self.catch_up_difficulty

        catch_up_actionable_from_day: Union[None, Unset, int]
        if isinstance(self.catch_up_actionable_from_day, Unset):
            catch_up_actionable_from_day = UNSET
        else:
            catch_up_actionable_from_day = self.catch_up_actionable_from_day

        catch_up_actionable_from_month: Union[None, Unset, int]
        if isinstance(self.catch_up_actionable_from_month, Unset):
            catch_up_actionable_from_month = UNSET
        else:
            catch_up_actionable_from_month = self.catch_up_actionable_from_month

        catch_up_due_at_day: Union[None, Unset, int]
        if isinstance(self.catch_up_due_at_day, Unset):
            catch_up_due_at_day = UNSET
        else:
            catch_up_due_at_day = self.catch_up_due_at_day

        catch_up_due_at_month: Union[None, Unset, int]
        if isinstance(self.catch_up_due_at_month, Unset):
            catch_up_due_at_month = UNSET
        else:
            catch_up_due_at_month = self.catch_up_due_at_month

        birthday: Union[None, Unset, str]
        if isinstance(self.birthday, Unset):
            birthday = UNSET
        else:
            birthday = self.birthday

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "relationship": relationship,
            }
        )
        if catch_up_period is not UNSET:
            field_dict["catch_up_period"] = catch_up_period
        if catch_up_eisen is not UNSET:
            field_dict["catch_up_eisen"] = catch_up_eisen
        if catch_up_difficulty is not UNSET:
            field_dict["catch_up_difficulty"] = catch_up_difficulty
        if catch_up_actionable_from_day is not UNSET:
            field_dict["catch_up_actionable_from_day"] = catch_up_actionable_from_day
        if catch_up_actionable_from_month is not UNSET:
            field_dict["catch_up_actionable_from_month"] = catch_up_actionable_from_month
        if catch_up_due_at_day is not UNSET:
            field_dict["catch_up_due_at_day"] = catch_up_due_at_day
        if catch_up_due_at_month is not UNSET:
            field_dict["catch_up_due_at_month"] = catch_up_due_at_month
        if birthday is not UNSET:
            field_dict["birthday"] = birthday

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        relationship = PersonRelationship(d.pop("relationship"))

        def _parse_catch_up_period(data: object) -> Union[None, RecurringTaskPeriod, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                catch_up_period_type_0 = RecurringTaskPeriod(data)

                return catch_up_period_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, RecurringTaskPeriod, Unset], data)

        catch_up_period = _parse_catch_up_period(d.pop("catch_up_period", UNSET))

        def _parse_catch_up_eisen(data: object) -> Union[Eisen, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                catch_up_eisen_type_0 = Eisen(data)

                return catch_up_eisen_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Eisen, None, Unset], data)

        catch_up_eisen = _parse_catch_up_eisen(d.pop("catch_up_eisen", UNSET))

        def _parse_catch_up_difficulty(data: object) -> Union[Difficulty, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                catch_up_difficulty_type_0 = Difficulty(data)

                return catch_up_difficulty_type_0
            except:  # noqa: E722
                pass
            return cast(Union[Difficulty, None, Unset], data)

        catch_up_difficulty = _parse_catch_up_difficulty(d.pop("catch_up_difficulty", UNSET))

        def _parse_catch_up_actionable_from_day(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        catch_up_actionable_from_day = _parse_catch_up_actionable_from_day(d.pop("catch_up_actionable_from_day", UNSET))

        def _parse_catch_up_actionable_from_month(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        catch_up_actionable_from_month = _parse_catch_up_actionable_from_month(
            d.pop("catch_up_actionable_from_month", UNSET)
        )

        def _parse_catch_up_due_at_day(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        catch_up_due_at_day = _parse_catch_up_due_at_day(d.pop("catch_up_due_at_day", UNSET))

        def _parse_catch_up_due_at_month(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        catch_up_due_at_month = _parse_catch_up_due_at_month(d.pop("catch_up_due_at_month", UNSET))

        def _parse_birthday(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        birthday = _parse_birthday(d.pop("birthday", UNSET))

        person_create_args = cls(
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

        person_create_args.additional_properties = d
        return person_create_args

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
