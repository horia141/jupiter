from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.difficulty import Difficulty
from ..models.score_source import ScoreSource
from ..types import UNSET, Unset

T = TypeVar("T", bound="ScoreLogEntry")


@_attrs_define
class ScoreLogEntry:
    """A record of a win or loss in accomplishing a task.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name for an entity which acts as both name and unique identifier.
        score_log_ref_id (str):
        source (ScoreSource): The source of a score.
        task_ref_id (str): A generic entity id.
        difficulty (Difficulty): The difficulty of a particular task.
        success (bool):
        score (int):
        archived_time (Union[None, Unset, str]):
        has_lucky_puppy_bonus (Union[None, Unset, bool]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    score_log_ref_id: str
    source: ScoreSource
    task_ref_id: str
    difficulty: Difficulty
    success: bool
    score: int
    archived_time: Union[None, Unset, str] = UNSET
    has_lucky_puppy_bonus: Union[None, Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        score_log_ref_id = self.score_log_ref_id

        source = self.source.value

        task_ref_id = self.task_ref_id

        difficulty = self.difficulty.value

        success = self.success

        score = self.score

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        has_lucky_puppy_bonus: Union[None, Unset, bool]
        if isinstance(self.has_lucky_puppy_bonus, Unset):
            has_lucky_puppy_bonus = UNSET
        else:
            has_lucky_puppy_bonus = self.has_lucky_puppy_bonus

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
                "score_log_ref_id": score_log_ref_id,
                "source": source,
                "task_ref_id": task_ref_id,
                "difficulty": difficulty,
                "success": success,
                "score": score,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if has_lucky_puppy_bonus is not UNSET:
            field_dict["has_lucky_puppy_bonus"] = has_lucky_puppy_bonus

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        score_log_ref_id = d.pop("score_log_ref_id")

        source = ScoreSource(d.pop("source"))

        task_ref_id = d.pop("task_ref_id")

        difficulty = Difficulty(d.pop("difficulty"))

        success = d.pop("success")

        score = d.pop("score")

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_has_lucky_puppy_bonus(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        has_lucky_puppy_bonus = _parse_has_lucky_puppy_bonus(d.pop("has_lucky_puppy_bonus", UNSET))

        score_log_entry = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            score_log_ref_id=score_log_ref_id,
            source=source,
            task_ref_id=task_ref_id,
            difficulty=difficulty,
            success=success,
            score=score,
            archived_time=archived_time,
            has_lucky_puppy_bonus=has_lucky_puppy_bonus,
        )

        score_log_entry.additional_properties = d
        return score_log_entry

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
