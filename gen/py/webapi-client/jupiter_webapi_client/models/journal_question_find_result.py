from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.journal_question import JournalQuestion
    from ..models.journal_question_find_result_order_of_questions import JournalQuestionFindResultOrderOfQuestions


T = TypeVar("T", bound="JournalQuestionFindResult")


@_attrs_define
class JournalQuestionFindResult:
    """JournalQuestionFind result.

    Attributes:
        questions (list[JournalQuestion]):
        order_of_questions (JournalQuestionFindResultOrderOfQuestions):
    """

    questions: list[JournalQuestion]
    order_of_questions: JournalQuestionFindResultOrderOfQuestions
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        questions = []
        for questions_item_data in self.questions:
            questions_item = questions_item_data.to_dict()
            questions.append(questions_item)

        order_of_questions = self.order_of_questions.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "questions": questions,
                "order_of_questions": order_of_questions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.journal_question import JournalQuestion  # noqa: PLC0415
        from ..models.journal_question_find_result_order_of_questions import JournalQuestionFindResultOrderOfQuestions  # noqa: PLC0415

        d = dict(src_dict)
        questions = []
        _questions = d.pop("questions")
        for questions_item_data in _questions:
            questions_item = JournalQuestion.from_dict(questions_item_data)

            questions.append(questions_item)

        order_of_questions = JournalQuestionFindResultOrderOfQuestions.from_dict(d.pop("order_of_questions"))

        journal_question_find_result = cls(
            questions=questions,
            order_of_questions=order_of_questions,
        )

        journal_question_find_result.additional_properties = d
        return journal_question_find_result

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
