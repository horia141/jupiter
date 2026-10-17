from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.person_update_args_catch_up_actionable_from_day import PersonUpdateArgsCatchUpActionableFromDay
    from ..models.person_update_args_catch_up_actionable_from_month import PersonUpdateArgsCatchUpActionableFromMonth
    from ..models.person_update_args_catch_up_difficulty import PersonUpdateArgsCatchUpDifficulty
    from ..models.person_update_args_catch_up_due_at_day import PersonUpdateArgsCatchUpDueAtDay
    from ..models.person_update_args_catch_up_due_at_month import PersonUpdateArgsCatchUpDueAtMonth
    from ..models.person_update_args_catch_up_eisen import PersonUpdateArgsCatchUpEisen
    from ..models.person_update_args_catch_up_period import PersonUpdateArgsCatchUpPeriod
    from ..models.person_update_args_circle_ref_ids import PersonUpdateArgsCircleRefIds
    from ..models.person_update_args_name import PersonUpdateArgsName
    from ..models.person_update_args_schedulability import PersonUpdateArgsSchedulability
    from ..models.person_update_args_scheduling_event_count import PersonUpdateArgsSchedulingEventCount
    from ..models.person_update_args_scheduling_event_duration_mins import PersonUpdateArgsSchedulingEventDurationMins


T = TypeVar("T", bound="PersonUpdateArgs")


@_attrs_define
class PersonUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        name (PersonUpdateArgsName):
        catch_up_period (PersonUpdateArgsCatchUpPeriod):
        catch_up_eisen (PersonUpdateArgsCatchUpEisen):
        catch_up_difficulty (PersonUpdateArgsCatchUpDifficulty):
        catch_up_actionable_from_day (PersonUpdateArgsCatchUpActionableFromDay):
        catch_up_actionable_from_month (PersonUpdateArgsCatchUpActionableFromMonth):
        catch_up_due_at_day (PersonUpdateArgsCatchUpDueAtDay):
        catch_up_due_at_month (PersonUpdateArgsCatchUpDueAtMonth):
        schedulability (PersonUpdateArgsSchedulability):
        scheduling_event_duration_mins (PersonUpdateArgsSchedulingEventDurationMins):
        scheduling_event_count (PersonUpdateArgsSchedulingEventCount):
        circle_ref_ids (PersonUpdateArgsCircleRefIds):
    """

    ref_id: str
    name: PersonUpdateArgsName
    catch_up_period: PersonUpdateArgsCatchUpPeriod
    catch_up_eisen: PersonUpdateArgsCatchUpEisen
    catch_up_difficulty: PersonUpdateArgsCatchUpDifficulty
    catch_up_actionable_from_day: PersonUpdateArgsCatchUpActionableFromDay
    catch_up_actionable_from_month: PersonUpdateArgsCatchUpActionableFromMonth
    catch_up_due_at_day: PersonUpdateArgsCatchUpDueAtDay
    catch_up_due_at_month: PersonUpdateArgsCatchUpDueAtMonth
    schedulability: PersonUpdateArgsSchedulability
    scheduling_event_duration_mins: PersonUpdateArgsSchedulingEventDurationMins
    scheduling_event_count: PersonUpdateArgsSchedulingEventCount
    circle_ref_ids: PersonUpdateArgsCircleRefIds
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        catch_up_period = self.catch_up_period.to_dict()

        catch_up_eisen = self.catch_up_eisen.to_dict()

        catch_up_difficulty = self.catch_up_difficulty.to_dict()

        catch_up_actionable_from_day = self.catch_up_actionable_from_day.to_dict()

        catch_up_actionable_from_month = self.catch_up_actionable_from_month.to_dict()

        catch_up_due_at_day = self.catch_up_due_at_day.to_dict()

        catch_up_due_at_month = self.catch_up_due_at_month.to_dict()

        schedulability = self.schedulability.to_dict()

        scheduling_event_duration_mins = self.scheduling_event_duration_mins.to_dict()

        scheduling_event_count = self.scheduling_event_count.to_dict()

        circle_ref_ids = self.circle_ref_ids.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "catch_up_period": catch_up_period,
                "catch_up_eisen": catch_up_eisen,
                "catch_up_difficulty": catch_up_difficulty,
                "catch_up_actionable_from_day": catch_up_actionable_from_day,
                "catch_up_actionable_from_month": catch_up_actionable_from_month,
                "catch_up_due_at_day": catch_up_due_at_day,
                "catch_up_due_at_month": catch_up_due_at_month,
                "schedulability": schedulability,
                "scheduling_event_duration_mins": scheduling_event_duration_mins,
                "scheduling_event_count": scheduling_event_count,
                "circle_ref_ids": circle_ref_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.person_update_args_catch_up_actionable_from_day import PersonUpdateArgsCatchUpActionableFromDay  # noqa: PLC0415
        from ..models.person_update_args_catch_up_actionable_from_month import (
            PersonUpdateArgsCatchUpActionableFromMonth,  # noqa: PLC0415
        )
        from ..models.person_update_args_catch_up_difficulty import PersonUpdateArgsCatchUpDifficulty  # noqa: PLC0415
        from ..models.person_update_args_catch_up_due_at_day import PersonUpdateArgsCatchUpDueAtDay  # noqa: PLC0415
        from ..models.person_update_args_catch_up_due_at_month import PersonUpdateArgsCatchUpDueAtMonth  # noqa: PLC0415
        from ..models.person_update_args_catch_up_eisen import PersonUpdateArgsCatchUpEisen  # noqa: PLC0415
        from ..models.person_update_args_catch_up_period import PersonUpdateArgsCatchUpPeriod  # noqa: PLC0415
        from ..models.person_update_args_circle_ref_ids import PersonUpdateArgsCircleRefIds  # noqa: PLC0415
        from ..models.person_update_args_name import PersonUpdateArgsName  # noqa: PLC0415
        from ..models.person_update_args_schedulability import PersonUpdateArgsSchedulability  # noqa: PLC0415
        from ..models.person_update_args_scheduling_event_count import PersonUpdateArgsSchedulingEventCount  # noqa: PLC0415
        from ..models.person_update_args_scheduling_event_duration_mins import (
            PersonUpdateArgsSchedulingEventDurationMins,  # noqa: PLC0415
        )

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = PersonUpdateArgsName.from_dict(d.pop("name"))

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

        schedulability = PersonUpdateArgsSchedulability.from_dict(d.pop("schedulability"))

        scheduling_event_duration_mins = PersonUpdateArgsSchedulingEventDurationMins.from_dict(
            d.pop("scheduling_event_duration_mins")
        )

        scheduling_event_count = PersonUpdateArgsSchedulingEventCount.from_dict(d.pop("scheduling_event_count"))

        circle_ref_ids = PersonUpdateArgsCircleRefIds.from_dict(d.pop("circle_ref_ids"))

        person_update_args = cls(
            ref_id=ref_id,
            name=name,
            catch_up_period=catch_up_period,
            catch_up_eisen=catch_up_eisen,
            catch_up_difficulty=catch_up_difficulty,
            catch_up_actionable_from_day=catch_up_actionable_from_day,
            catch_up_actionable_from_month=catch_up_actionable_from_month,
            catch_up_due_at_day=catch_up_due_at_day,
            catch_up_due_at_month=catch_up_due_at_month,
            schedulability=schedulability,
            scheduling_event_duration_mins=scheduling_event_duration_mins,
            scheduling_event_count=scheduling_event_count,
            circle_ref_ids=circle_ref_ids,
        )

        person_update_args.additional_properties = d
        return person_update_args

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
