from typing import Any, Dict, List, Type, TypeVar, Union

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
        catch_up_period (Union[Unset, RecurringTaskPeriod]): A period for a particular task.
        catch_up_eisen (Union[Unset, Eisen]): The Eisenhower status of a particular task.
        catch_up_difficulty (Union[Unset, Difficulty]): The difficulty of a particular task.
        catch_up_actionable_from_day (Union[Unset, int]): The due day for a recurring task.
        catch_up_actionable_from_month (Union[Unset, int]): The due month for a recurring task.
        catch_up_due_at_day (Union[Unset, int]): The due day for a recurring task.
        catch_up_due_at_month (Union[Unset, int]): The due month for a recurring task.
        birthday (Union[Unset, str]): The birthday of a person.
    """

    name: str
    relationship: PersonRelationship
    catch_up_period: Union[Unset, RecurringTaskPeriod] = UNSET
    catch_up_eisen: Union[Unset, Eisen] = UNSET
    catch_up_difficulty: Union[Unset, Difficulty] = UNSET
    catch_up_actionable_from_day: Union[Unset, int] = UNSET
    catch_up_actionable_from_month: Union[Unset, int] = UNSET
    catch_up_due_at_day: Union[Unset, int] = UNSET
    catch_up_due_at_month: Union[Unset, int] = UNSET
    birthday: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        relationship = self.relationship.value

        catch_up_period: Union[Unset, str] = UNSET
        if not isinstance(self.catch_up_period, Unset):
            catch_up_period = self.catch_up_period.value

        catch_up_eisen: Union[Unset, str] = UNSET
        if not isinstance(self.catch_up_eisen, Unset):
            catch_up_eisen = self.catch_up_eisen.value

        catch_up_difficulty: Union[Unset, str] = UNSET
        if not isinstance(self.catch_up_difficulty, Unset):
            catch_up_difficulty = self.catch_up_difficulty.value

        catch_up_actionable_from_day = self.catch_up_actionable_from_day

        catch_up_actionable_from_month = self.catch_up_actionable_from_month

        catch_up_due_at_day = self.catch_up_due_at_day

        catch_up_due_at_month = self.catch_up_due_at_month

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

        _catch_up_period = d.pop("catch_up_period", UNSET)
        catch_up_period: Union[Unset, RecurringTaskPeriod]
        if isinstance(_catch_up_period, Unset):
            catch_up_period = UNSET
        else:
            catch_up_period = RecurringTaskPeriod(_catch_up_period)

        _catch_up_eisen = d.pop("catch_up_eisen", UNSET)
        catch_up_eisen: Union[Unset, Eisen]
        if isinstance(_catch_up_eisen, Unset):
            catch_up_eisen = UNSET
        else:
            catch_up_eisen = Eisen(_catch_up_eisen)

        _catch_up_difficulty = d.pop("catch_up_difficulty", UNSET)
        catch_up_difficulty: Union[Unset, Difficulty]
        if isinstance(_catch_up_difficulty, Unset):
            catch_up_difficulty = UNSET
        else:
            catch_up_difficulty = Difficulty(_catch_up_difficulty)

        catch_up_actionable_from_day = d.pop("catch_up_actionable_from_day", UNSET)

        catch_up_actionable_from_month = d.pop("catch_up_actionable_from_month", UNSET)

        catch_up_due_at_day = d.pop("catch_up_due_at_day", UNSET)

        catch_up_due_at_month = d.pop("catch_up_due_at_month", UNSET)

        birthday = d.pop("birthday", UNSET)

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
