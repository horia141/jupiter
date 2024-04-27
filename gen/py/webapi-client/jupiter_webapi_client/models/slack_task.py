from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.push_generation_extra_info import PushGenerationExtraInfo


T = TypeVar("T", bound="SlackTask")


@_attrs_define
class SlackTask:
    """A Slack task which needs to be converted into an inbox task.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name for an entity which acts as both name and unique identifier.
        slack_task_collection_ref_id (str):
        user (str): A Slack user name.
        message (str):
        generation_extra_info (PushGenerationExtraInfo): Extra information for how to generate an inbox task.
        has_generated_task (bool):
        archived_time (Union[None, Unset, str]):
        channel (Union[None, Unset, str]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    slack_task_collection_ref_id: str
    user: str
    message: str
    generation_extra_info: "PushGenerationExtraInfo"
    has_generated_task: bool
    archived_time: Union[None, Unset, str] = UNSET
    channel: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        slack_task_collection_ref_id = self.slack_task_collection_ref_id

        user = self.user

        message = self.message

        generation_extra_info = self.generation_extra_info.to_dict()

        has_generated_task = self.has_generated_task

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        channel: Union[None, Unset, str]
        if isinstance(self.channel, Unset):
            channel = UNSET
        else:
            channel = self.channel

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "slack_task_collection_ref_id": slack_task_collection_ref_id,
                "user": user,
                "message": message,
                "generation_extra_info": generation_extra_info,
                "has_generated_task": has_generated_task,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if channel is not UNSET:
            field_dict["channel"] = channel

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.push_generation_extra_info import PushGenerationExtraInfo

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        slack_task_collection_ref_id = d.pop("slack_task_collection_ref_id")

        user = d.pop("user")

        message = d.pop("message")

        generation_extra_info = PushGenerationExtraInfo.from_dict(d.pop("generation_extra_info"))

        has_generated_task = d.pop("has_generated_task")

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_channel(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        channel = _parse_channel(d.pop("channel", UNSET))

        slack_task = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            slack_task_collection_ref_id=slack_task_collection_ref_id,
            user=user,
            message=message,
            generation_extra_info=generation_extra_info,
            has_generated_task=has_generated_task,
            archived_time=archived_time,
            channel=channel,
        )

        slack_task.additional_properties = d
        return slack_task

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
