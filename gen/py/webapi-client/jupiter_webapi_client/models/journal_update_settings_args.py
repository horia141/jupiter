from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.journal_update_settings_args_generation_approach import JournalUpdateSettingsArgsGenerationApproach
    from ..models.journal_update_settings_args_generation_in_advance_days import (
        JournalUpdateSettingsArgsGenerationInAdvanceDays,
    )
    from ..models.journal_update_settings_args_periods import JournalUpdateSettingsArgsPeriods
    from ..models.journal_update_settings_args_writing_task_difficulty import (
        JournalUpdateSettingsArgsWritingTaskDifficulty,
    )
    from ..models.journal_update_settings_args_writing_task_eisen import JournalUpdateSettingsArgsWritingTaskEisen
    from ..models.journal_update_settings_args_writing_task_project_ref_id import (
        JournalUpdateSettingsArgsWritingTaskProjectRefId,
    )


T = TypeVar("T", bound="JournalUpdateSettingsArgs")


@_attrs_define
class JournalUpdateSettingsArgs:
    """Args.

    Attributes:
        periods (JournalUpdateSettingsArgsPeriods):
        generation_approach (JournalUpdateSettingsArgsGenerationApproach):
        generation_in_advance_days (JournalUpdateSettingsArgsGenerationInAdvanceDays):
        writing_task_project_ref_id (JournalUpdateSettingsArgsWritingTaskProjectRefId):
        writing_task_eisen (JournalUpdateSettingsArgsWritingTaskEisen):
        writing_task_difficulty (JournalUpdateSettingsArgsWritingTaskDifficulty):
    """

    periods: "JournalUpdateSettingsArgsPeriods"
    generation_approach: "JournalUpdateSettingsArgsGenerationApproach"
    generation_in_advance_days: "JournalUpdateSettingsArgsGenerationInAdvanceDays"
    writing_task_project_ref_id: "JournalUpdateSettingsArgsWritingTaskProjectRefId"
    writing_task_eisen: "JournalUpdateSettingsArgsWritingTaskEisen"
    writing_task_difficulty: "JournalUpdateSettingsArgsWritingTaskDifficulty"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        periods = self.periods.to_dict()

        generation_approach = self.generation_approach.to_dict()

        generation_in_advance_days = self.generation_in_advance_days.to_dict()

        writing_task_project_ref_id = self.writing_task_project_ref_id.to_dict()

        writing_task_eisen = self.writing_task_eisen.to_dict()

        writing_task_difficulty = self.writing_task_difficulty.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "periods": periods,
                "generation_approach": generation_approach,
                "generation_in_advance_days": generation_in_advance_days,
                "writing_task_project_ref_id": writing_task_project_ref_id,
                "writing_task_eisen": writing_task_eisen,
                "writing_task_difficulty": writing_task_difficulty,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.journal_update_settings_args_generation_approach import (
            JournalUpdateSettingsArgsGenerationApproach,
        )
        from ..models.journal_update_settings_args_generation_in_advance_days import (
            JournalUpdateSettingsArgsGenerationInAdvanceDays,
        )
        from ..models.journal_update_settings_args_periods import JournalUpdateSettingsArgsPeriods
        from ..models.journal_update_settings_args_writing_task_difficulty import (
            JournalUpdateSettingsArgsWritingTaskDifficulty,
        )
        from ..models.journal_update_settings_args_writing_task_eisen import JournalUpdateSettingsArgsWritingTaskEisen
        from ..models.journal_update_settings_args_writing_task_project_ref_id import (
            JournalUpdateSettingsArgsWritingTaskProjectRefId,
        )

        d = dict(src_dict)
        periods = JournalUpdateSettingsArgsPeriods.from_dict(d.pop("periods"))

        generation_approach = JournalUpdateSettingsArgsGenerationApproach.from_dict(d.pop("generation_approach"))

        generation_in_advance_days = JournalUpdateSettingsArgsGenerationInAdvanceDays.from_dict(
            d.pop("generation_in_advance_days")
        )

        writing_task_project_ref_id = JournalUpdateSettingsArgsWritingTaskProjectRefId.from_dict(
            d.pop("writing_task_project_ref_id")
        )

        writing_task_eisen = JournalUpdateSettingsArgsWritingTaskEisen.from_dict(d.pop("writing_task_eisen"))

        writing_task_difficulty = JournalUpdateSettingsArgsWritingTaskDifficulty.from_dict(
            d.pop("writing_task_difficulty")
        )

        journal_update_settings_args = cls(
            periods=periods,
            generation_approach=generation_approach,
            generation_in_advance_days=generation_in_advance_days,
            writing_task_project_ref_id=writing_task_project_ref_id,
            writing_task_eisen=writing_task_eisen,
            writing_task_difficulty=writing_task_difficulty,
        )

        journal_update_settings_args.additional_properties = d
        return journal_update_settings_args

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
