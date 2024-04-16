from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.push_generation_extra_info import PushGenerationExtraInfo


T = TypeVar("T", bound="EmailTask")


@_attrs_define
class EmailTask:
    """An email task which needs to be converted into an inbox task.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name for an entity which acts as both name and unique identifier.
        email_task_collection (str):
        from_address (str): An email address.
        from_name (str): An email user name.
        to_address (str): An email address.
        subject (str):
        body (str):
        generation_extra_info (PushGenerationExtraInfo): Extra information for how to generate an inbox task.
        has_generated_task (bool):
        archived_time (Union[Unset, str]): A timestamp in the application.
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    email_task_collection: str
    from_address: str
    from_name: str
    to_address: str
    subject: str
    body: str
    generation_extra_info: "PushGenerationExtraInfo"
    has_generated_task: bool
    archived_time: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        email_task_collection = self.email_task_collection

        from_address = self.from_address

        from_name = self.from_name

        to_address = self.to_address

        subject = self.subject

        body = self.body

        generation_extra_info = self.generation_extra_info.to_dict()

        has_generated_task = self.has_generated_task

        archived_time = self.archived_time

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
                "email_task_collection": email_task_collection,
                "from_address": from_address,
                "from_name": from_name,
                "to_address": to_address,
                "subject": subject,
                "body": body,
                "generation_extra_info": generation_extra_info,
                "has_generated_task": has_generated_task,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time

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

        email_task_collection = d.pop("email_task_collection")

        from_address = d.pop("from_address")

        from_name = d.pop("from_name")

        to_address = d.pop("to_address")

        subject = d.pop("subject")

        body = d.pop("body")

        generation_extra_info = PushGenerationExtraInfo.from_dict(d.pop("generation_extra_info"))

        has_generated_task = d.pop("has_generated_task")

        archived_time = d.pop("archived_time", UNSET)

        email_task = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            email_task_collection=email_task_collection,
            from_address=from_address,
            from_name=from_name,
            to_address=to_address,
            subject=subject,
            body=body,
            generation_extra_info=generation_extra_info,
            has_generated_task=has_generated_task,
            archived_time=archived_time,
        )

        email_task.additional_properties = d
        return email_task

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
