from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.slack_task_update_args_channel import SlackTaskUpdateArgsChannel
    from ..models.slack_task_update_args_generation_actionable_date import SlackTaskUpdateArgsGenerationActionableDate
    from ..models.slack_task_update_args_generation_difficulty import SlackTaskUpdateArgsGenerationDifficulty
    from ..models.slack_task_update_args_generation_due_date import SlackTaskUpdateArgsGenerationDueDate
    from ..models.slack_task_update_args_generation_eisen import SlackTaskUpdateArgsGenerationEisen
    from ..models.slack_task_update_args_generation_name import SlackTaskUpdateArgsGenerationName
    from ..models.slack_task_update_args_generation_status import SlackTaskUpdateArgsGenerationStatus
    from ..models.slack_task_update_args_message import SlackTaskUpdateArgsMessage
    from ..models.slack_task_update_args_user import SlackTaskUpdateArgsUser


T = TypeVar("T", bound="SlackTaskUpdateArgs")


@_attrs_define
class SlackTaskUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        user (SlackTaskUpdateArgsUser):
        channel (SlackTaskUpdateArgsChannel):
        message (SlackTaskUpdateArgsMessage):
        generation_name (SlackTaskUpdateArgsGenerationName):
        generation_status (SlackTaskUpdateArgsGenerationStatus):
        generation_eisen (SlackTaskUpdateArgsGenerationEisen):
        generation_difficulty (SlackTaskUpdateArgsGenerationDifficulty):
        generation_actionable_date (SlackTaskUpdateArgsGenerationActionableDate):
        generation_due_date (SlackTaskUpdateArgsGenerationDueDate):
    """

    ref_id: str
    user: "SlackTaskUpdateArgsUser"
    channel: "SlackTaskUpdateArgsChannel"
    message: "SlackTaskUpdateArgsMessage"
    generation_name: "SlackTaskUpdateArgsGenerationName"
    generation_status: "SlackTaskUpdateArgsGenerationStatus"
    generation_eisen: "SlackTaskUpdateArgsGenerationEisen"
    generation_difficulty: "SlackTaskUpdateArgsGenerationDifficulty"
    generation_actionable_date: "SlackTaskUpdateArgsGenerationActionableDate"
    generation_due_date: "SlackTaskUpdateArgsGenerationDueDate"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        user = self.user.to_dict()

        channel = self.channel.to_dict()

        message = self.message.to_dict()

        generation_name = self.generation_name.to_dict()

        generation_status = self.generation_status.to_dict()

        generation_eisen = self.generation_eisen.to_dict()

        generation_difficulty = self.generation_difficulty.to_dict()

        generation_actionable_date = self.generation_actionable_date.to_dict()

        generation_due_date = self.generation_due_date.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "user": user,
                "channel": channel,
                "message": message,
                "generation_name": generation_name,
                "generation_status": generation_status,
                "generation_eisen": generation_eisen,
                "generation_difficulty": generation_difficulty,
                "generation_actionable_date": generation_actionable_date,
                "generation_due_date": generation_due_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.slack_task_update_args_channel import SlackTaskUpdateArgsChannel
        from ..models.slack_task_update_args_generation_actionable_date import (
            SlackTaskUpdateArgsGenerationActionableDate,
        )
        from ..models.slack_task_update_args_generation_difficulty import SlackTaskUpdateArgsGenerationDifficulty
        from ..models.slack_task_update_args_generation_due_date import SlackTaskUpdateArgsGenerationDueDate
        from ..models.slack_task_update_args_generation_eisen import SlackTaskUpdateArgsGenerationEisen
        from ..models.slack_task_update_args_generation_name import SlackTaskUpdateArgsGenerationName
        from ..models.slack_task_update_args_generation_status import SlackTaskUpdateArgsGenerationStatus
        from ..models.slack_task_update_args_message import SlackTaskUpdateArgsMessage
        from ..models.slack_task_update_args_user import SlackTaskUpdateArgsUser

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        user = SlackTaskUpdateArgsUser.from_dict(d.pop("user"))

        channel = SlackTaskUpdateArgsChannel.from_dict(d.pop("channel"))

        message = SlackTaskUpdateArgsMessage.from_dict(d.pop("message"))

        generation_name = SlackTaskUpdateArgsGenerationName.from_dict(d.pop("generation_name"))

        generation_status = SlackTaskUpdateArgsGenerationStatus.from_dict(d.pop("generation_status"))

        generation_eisen = SlackTaskUpdateArgsGenerationEisen.from_dict(d.pop("generation_eisen"))

        generation_difficulty = SlackTaskUpdateArgsGenerationDifficulty.from_dict(d.pop("generation_difficulty"))

        generation_actionable_date = SlackTaskUpdateArgsGenerationActionableDate.from_dict(
            d.pop("generation_actionable_date")
        )

        generation_due_date = SlackTaskUpdateArgsGenerationDueDate.from_dict(d.pop("generation_due_date"))

        slack_task_update_args = cls(
            ref_id=ref_id,
            user=user,
            channel=channel,
            message=message,
            generation_name=generation_name,
            generation_status=generation_status,
            generation_eisen=generation_eisen,
            generation_difficulty=generation_difficulty,
            generation_actionable_date=generation_actionable_date,
            generation_due_date=generation_due_date,
        )

        slack_task_update_args.additional_properties = d
        return slack_task_update_args

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
