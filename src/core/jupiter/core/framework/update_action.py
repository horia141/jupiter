"""The update action for a field."""
import typing
from typing import Callable, Final, Generic, Optional, TypeVar

from pydantic import ValidationError
from pydantic.fields import ModelField

UpdateActionT = TypeVar("UpdateActionT")
NewT = TypeVar("NewT")


class UpdateAction(Generic[UpdateActionT]):
    """The update action for a field."""

    _should_change: Final[bool]
    _value: Optional[UpdateActionT] = None

    def __init__(
        self,
        should_change: bool,
        value: Optional[UpdateActionT] = None,
    ) -> None:
        """Constructor."""
        self._should_change = should_change
        self._value = value

    @staticmethod
    def do_nothing() -> "UpdateAction[UpdateActionT]":
        """An update action where nothing needs to happen."""
        return UpdateAction[UpdateActionT](should_change=False)

    @staticmethod
    def change_to(value: UpdateActionT) -> "UpdateAction[UpdateActionT]":
        """An update action where the value needs to be changed to a new value."""
        return UpdateAction[UpdateActionT](should_change=True, value=value)

    def or_else(self, value_if_should_not_change: UpdateActionT) -> UpdateActionT:
        """Return the value of the action if it should change or the argument if it should not."""
        if self._should_change:
            return typing.cast(UpdateActionT, self._value)
        else:
            return value_if_should_not_change

    def transform(
        self, transform: Callable[[UpdateActionT], NewT]
    ) -> "UpdateAction[NewT]":
        """Transform the value of an update action if it is present."""
        if self._should_change:
            return UpdateAction.change_to(transform(self.just_the_value))
        else:
            return UpdateAction.do_nothing()

    @property
    def just_the_value(self) -> UpdateActionT:
        """Return the value if it exists."""
        if not self._should_change:
            raise Exception("Trying to get the value when it's not there")
        return typing.cast(UpdateActionT, self._value)

    @property
    def should_change(self) -> bool:
        """Whether this represents an action for change or not."""
        return self._should_change

    def __repr__(self) -> str:
        """The representation of this action."""
        if self._should_change:
            return f"UpdateAction.change_to({repr(self._value)})"
        else:
            return "UpdateAction.do_nothing()"
