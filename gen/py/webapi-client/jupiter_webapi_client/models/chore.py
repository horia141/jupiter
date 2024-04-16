from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.recurring_task_gen_params import RecurringTaskGenParams


T = TypeVar("T", bound="Chore")


@_attrs_define
class Chore:
    """A chore.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The chore name.
        chore_collection (str):
        project_ref_id (str): A generic entity id.
        gen_params (RecurringTaskGenParams): Parameters for metric collection.
        suspended (bool):
        must_do (bool):
        start_at_date (str): A date or possibly a datetime for the application.
        archived_time (Union[Unset, str]): A timestamp in the application.
        end_at_date (Union[Unset, str]): A date or possibly a datetime for the application.
        skip_rule (Union[Unset, str]): The rules for skipping a recurring task.
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    chore_collection: str
    project_ref_id: str
    gen_params: "RecurringTaskGenParams"
    suspended: bool
    must_do: bool
    start_at_date: str
    archived_time: Union[Unset, str] = UNSET
    end_at_date: Union[Unset, str] = UNSET
    skip_rule: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        chore_collection = self.chore_collection

        project_ref_id = self.project_ref_id

        gen_params = self.gen_params.to_dict()

        suspended = self.suspended

        must_do = self.must_do

        start_at_date = self.start_at_date

        archived_time = self.archived_time

        end_at_date = self.end_at_date

        skip_rule = self.skip_rule

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
                "chore_collection": chore_collection,
                "project_ref_id": project_ref_id,
                "gen_params": gen_params,
                "suspended": suspended,
                "must_do": must_do,
                "start_at_date": start_at_date,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if end_at_date is not UNSET:
            field_dict["end_at_date"] = end_at_date
        if skip_rule is not UNSET:
            field_dict["skip_rule"] = skip_rule

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.recurring_task_gen_params import RecurringTaskGenParams

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        chore_collection = d.pop("chore_collection")

        project_ref_id = d.pop("project_ref_id")

        gen_params = RecurringTaskGenParams.from_dict(d.pop("gen_params"))

        suspended = d.pop("suspended")

        must_do = d.pop("must_do")

        start_at_date = d.pop("start_at_date")

        archived_time = d.pop("archived_time", UNSET)

        end_at_date = d.pop("end_at_date", UNSET)

        skip_rule = d.pop("skip_rule", UNSET)

        chore = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            chore_collection=chore_collection,
            project_ref_id=project_ref_id,
            gen_params=gen_params,
            suspended=suspended,
            must_do=must_do,
            start_at_date=start_at_date,
            archived_time=archived_time,
            end_at_date=end_at_date,
            skip_rule=skip_rule,
        )

        chore.additional_properties = d
        return chore

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
