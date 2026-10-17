from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.email_task_update_args_body import EmailTaskUpdateArgsBody
    from ..models.email_task_update_args_from_address import EmailTaskUpdateArgsFromAddress
    from ..models.email_task_update_args_from_name import EmailTaskUpdateArgsFromName
    from ..models.email_task_update_args_generation_actionable_date import EmailTaskUpdateArgsGenerationActionableDate
    from ..models.email_task_update_args_generation_difficulty import EmailTaskUpdateArgsGenerationDifficulty
    from ..models.email_task_update_args_generation_due_date import EmailTaskUpdateArgsGenerationDueDate
    from ..models.email_task_update_args_generation_eisen import EmailTaskUpdateArgsGenerationEisen
    from ..models.email_task_update_args_generation_name import EmailTaskUpdateArgsGenerationName
    from ..models.email_task_update_args_generation_status import EmailTaskUpdateArgsGenerationStatus
    from ..models.email_task_update_args_schedulability import EmailTaskUpdateArgsSchedulability
    from ..models.email_task_update_args_scheduling_event_count import EmailTaskUpdateArgsSchedulingEventCount
    from ..models.email_task_update_args_scheduling_event_duration_mins import (
        EmailTaskUpdateArgsSchedulingEventDurationMins,
    )
    from ..models.email_task_update_args_subject import EmailTaskUpdateArgsSubject
    from ..models.email_task_update_args_to_address import EmailTaskUpdateArgsToAddress


T = TypeVar("T", bound="EmailTaskUpdateArgs")


@_attrs_define
class EmailTaskUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        from_address (EmailTaskUpdateArgsFromAddress):
        from_name (EmailTaskUpdateArgsFromName):
        to_address (EmailTaskUpdateArgsToAddress):
        subject (EmailTaskUpdateArgsSubject):
        body (EmailTaskUpdateArgsBody):
        generation_name (EmailTaskUpdateArgsGenerationName):
        generation_status (EmailTaskUpdateArgsGenerationStatus):
        generation_eisen (EmailTaskUpdateArgsGenerationEisen):
        generation_difficulty (EmailTaskUpdateArgsGenerationDifficulty):
        generation_actionable_date (EmailTaskUpdateArgsGenerationActionableDate):
        generation_due_date (EmailTaskUpdateArgsGenerationDueDate):
        schedulability (EmailTaskUpdateArgsSchedulability):
        scheduling_event_duration_mins (EmailTaskUpdateArgsSchedulingEventDurationMins):
        scheduling_event_count (EmailTaskUpdateArgsSchedulingEventCount):
    """

    ref_id: str
    from_address: EmailTaskUpdateArgsFromAddress
    from_name: EmailTaskUpdateArgsFromName
    to_address: EmailTaskUpdateArgsToAddress
    subject: EmailTaskUpdateArgsSubject
    body: EmailTaskUpdateArgsBody
    generation_name: EmailTaskUpdateArgsGenerationName
    generation_status: EmailTaskUpdateArgsGenerationStatus
    generation_eisen: EmailTaskUpdateArgsGenerationEisen
    generation_difficulty: EmailTaskUpdateArgsGenerationDifficulty
    generation_actionable_date: EmailTaskUpdateArgsGenerationActionableDate
    generation_due_date: EmailTaskUpdateArgsGenerationDueDate
    schedulability: EmailTaskUpdateArgsSchedulability
    scheduling_event_duration_mins: EmailTaskUpdateArgsSchedulingEventDurationMins
    scheduling_event_count: EmailTaskUpdateArgsSchedulingEventCount
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        from_address = self.from_address.to_dict()

        from_name = self.from_name.to_dict()

        to_address = self.to_address.to_dict()

        subject = self.subject.to_dict()

        body = self.body.to_dict()

        generation_name = self.generation_name.to_dict()

        generation_status = self.generation_status.to_dict()

        generation_eisen = self.generation_eisen.to_dict()

        generation_difficulty = self.generation_difficulty.to_dict()

        generation_actionable_date = self.generation_actionable_date.to_dict()

        generation_due_date = self.generation_due_date.to_dict()

        schedulability = self.schedulability.to_dict()

        scheduling_event_duration_mins = self.scheduling_event_duration_mins.to_dict()

        scheduling_event_count = self.scheduling_event_count.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "from_address": from_address,
                "from_name": from_name,
                "to_address": to_address,
                "subject": subject,
                "body": body,
                "generation_name": generation_name,
                "generation_status": generation_status,
                "generation_eisen": generation_eisen,
                "generation_difficulty": generation_difficulty,
                "generation_actionable_date": generation_actionable_date,
                "generation_due_date": generation_due_date,
                "schedulability": schedulability,
                "scheduling_event_duration_mins": scheduling_event_duration_mins,
                "scheduling_event_count": scheduling_event_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.email_task_update_args_body import EmailTaskUpdateArgsBody  # noqa: PLC0415
        from ..models.email_task_update_args_from_address import EmailTaskUpdateArgsFromAddress  # noqa: PLC0415
        from ..models.email_task_update_args_from_name import EmailTaskUpdateArgsFromName  # noqa: PLC0415
        from ..models.email_task_update_args_generation_actionable_date import (
            EmailTaskUpdateArgsGenerationActionableDate,  # noqa: PLC0415
        )
        from ..models.email_task_update_args_generation_difficulty import EmailTaskUpdateArgsGenerationDifficulty  # noqa: PLC0415
        from ..models.email_task_update_args_generation_due_date import EmailTaskUpdateArgsGenerationDueDate  # noqa: PLC0415
        from ..models.email_task_update_args_generation_eisen import EmailTaskUpdateArgsGenerationEisen  # noqa: PLC0415
        from ..models.email_task_update_args_generation_name import EmailTaskUpdateArgsGenerationName  # noqa: PLC0415
        from ..models.email_task_update_args_generation_status import EmailTaskUpdateArgsGenerationStatus  # noqa: PLC0415
        from ..models.email_task_update_args_schedulability import EmailTaskUpdateArgsSchedulability  # noqa: PLC0415
        from ..models.email_task_update_args_scheduling_event_count import EmailTaskUpdateArgsSchedulingEventCount  # noqa: PLC0415
        from ..models.email_task_update_args_scheduling_event_duration_mins import (
            EmailTaskUpdateArgsSchedulingEventDurationMins,  # noqa: PLC0415
        )
        from ..models.email_task_update_args_subject import EmailTaskUpdateArgsSubject  # noqa: PLC0415
        from ..models.email_task_update_args_to_address import EmailTaskUpdateArgsToAddress  # noqa: PLC0415

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        from_address = EmailTaskUpdateArgsFromAddress.from_dict(d.pop("from_address"))

        from_name = EmailTaskUpdateArgsFromName.from_dict(d.pop("from_name"))

        to_address = EmailTaskUpdateArgsToAddress.from_dict(d.pop("to_address"))

        subject = EmailTaskUpdateArgsSubject.from_dict(d.pop("subject"))

        body = EmailTaskUpdateArgsBody.from_dict(d.pop("body"))

        generation_name = EmailTaskUpdateArgsGenerationName.from_dict(d.pop("generation_name"))

        generation_status = EmailTaskUpdateArgsGenerationStatus.from_dict(d.pop("generation_status"))

        generation_eisen = EmailTaskUpdateArgsGenerationEisen.from_dict(d.pop("generation_eisen"))

        generation_difficulty = EmailTaskUpdateArgsGenerationDifficulty.from_dict(d.pop("generation_difficulty"))

        generation_actionable_date = EmailTaskUpdateArgsGenerationActionableDate.from_dict(
            d.pop("generation_actionable_date")
        )

        generation_due_date = EmailTaskUpdateArgsGenerationDueDate.from_dict(d.pop("generation_due_date"))

        schedulability = EmailTaskUpdateArgsSchedulability.from_dict(d.pop("schedulability"))

        scheduling_event_duration_mins = EmailTaskUpdateArgsSchedulingEventDurationMins.from_dict(
            d.pop("scheduling_event_duration_mins")
        )

        scheduling_event_count = EmailTaskUpdateArgsSchedulingEventCount.from_dict(d.pop("scheduling_event_count"))

        email_task_update_args = cls(
            ref_id=ref_id,
            from_address=from_address,
            from_name=from_name,
            to_address=to_address,
            subject=subject,
            body=body,
            generation_name=generation_name,
            generation_status=generation_status,
            generation_eisen=generation_eisen,
            generation_difficulty=generation_difficulty,
            generation_actionable_date=generation_actionable_date,
            generation_due_date=generation_due_date,
            schedulability=schedulability,
            scheduling_event_duration_mins=scheduling_event_duration_mins,
            scheduling_event_count=scheduling_event_count,
        )

        email_task_update_args.additional_properties = d
        return email_task_update_args

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
