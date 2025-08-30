from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.journal_generation_approach import JournalGenerationApproach
from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.journal_collection_generation_in_advance_days import JournalCollectionGenerationInAdvanceDays
    from ..models.recurring_task_gen_params import RecurringTaskGenParams


T = TypeVar("T", bound="JournalCollection")


@_attrs_define
class JournalCollection:
    """A journal.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        workspace_ref_id (str):
        periods (list[RecurringTaskPeriod]):
        generation_approach (JournalGenerationApproach): The approach to generate journals.
        generation_in_advance_days (JournalCollectionGenerationInAdvanceDays):
        writing_task_project_ref_id (str): A generic entity id.
        archival_reason (Union[None, Unset, str]):
        archived_time (Union[None, Unset, str]):
        writing_task_gen_params (Union['RecurringTaskGenParams', None, Unset]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    workspace_ref_id: str
    periods: list[RecurringTaskPeriod]
    generation_approach: JournalGenerationApproach
    generation_in_advance_days: "JournalCollectionGenerationInAdvanceDays"
    writing_task_project_ref_id: str
    archival_reason: Union[None, Unset, str] = UNSET
    archived_time: Union[None, Unset, str] = UNSET
    writing_task_gen_params: Union["RecurringTaskGenParams", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.recurring_task_gen_params import RecurringTaskGenParams

        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        workspace_ref_id = self.workspace_ref_id

        periods = []
        for periods_item_data in self.periods:
            periods_item = periods_item_data.value
            periods.append(periods_item)

        generation_approach = self.generation_approach.value

        generation_in_advance_days = self.generation_in_advance_days.to_dict()

        writing_task_project_ref_id = self.writing_task_project_ref_id

        archival_reason: Union[None, Unset, str]
        if isinstance(self.archival_reason, Unset):
            archival_reason = UNSET
        else:
            archival_reason = self.archival_reason

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        writing_task_gen_params: Union[None, Unset, dict[str, Any]]
        if isinstance(self.writing_task_gen_params, Unset):
            writing_task_gen_params = UNSET
        elif isinstance(self.writing_task_gen_params, RecurringTaskGenParams):
            writing_task_gen_params = self.writing_task_gen_params.to_dict()
        else:
            writing_task_gen_params = self.writing_task_gen_params

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "workspace_ref_id": workspace_ref_id,
                "periods": periods,
                "generation_approach": generation_approach,
                "generation_in_advance_days": generation_in_advance_days,
                "writing_task_project_ref_id": writing_task_project_ref_id,
            }
        )
        if archival_reason is not UNSET:
            field_dict["archival_reason"] = archival_reason
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if writing_task_gen_params is not UNSET:
            field_dict["writing_task_gen_params"] = writing_task_gen_params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.journal_collection_generation_in_advance_days import JournalCollectionGenerationInAdvanceDays
        from ..models.recurring_task_gen_params import RecurringTaskGenParams

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        workspace_ref_id = d.pop("workspace_ref_id")

        periods = []
        _periods = d.pop("periods")
        for periods_item_data in _periods:
            periods_item = RecurringTaskPeriod(periods_item_data)

            periods.append(periods_item)

        generation_approach = JournalGenerationApproach(d.pop("generation_approach"))

        generation_in_advance_days = JournalCollectionGenerationInAdvanceDays.from_dict(
            d.pop("generation_in_advance_days")
        )

        writing_task_project_ref_id = d.pop("writing_task_project_ref_id")

        def _parse_archival_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archival_reason = _parse_archival_reason(d.pop("archival_reason", UNSET))

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_writing_task_gen_params(data: object) -> Union["RecurringTaskGenParams", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                writing_task_gen_params_type_0 = RecurringTaskGenParams.from_dict(data)

                return writing_task_gen_params_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RecurringTaskGenParams", None, Unset], data)

        writing_task_gen_params = _parse_writing_task_gen_params(d.pop("writing_task_gen_params", UNSET))

        journal_collection = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            workspace_ref_id=workspace_ref_id,
            periods=periods,
            generation_approach=generation_approach,
            generation_in_advance_days=generation_in_advance_days,
            writing_task_project_ref_id=writing_task_project_ref_id,
            archival_reason=archival_reason,
            archived_time=archived_time,
            writing_task_gen_params=writing_task_gen_params,
        )

        journal_collection.additional_properties = d
        return journal_collection

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
