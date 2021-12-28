"""The update action for a field."""
import typing
from typing import TypeVar, Generic, Final, Optional

UpdateActionType = TypeVar('UpdateActionType')


class UpdateAction(Generic[UpdateActionType]):
    """The update action for a field."""

    _should_change: Final[bool]
    _value: Optional[UpdateActionType]

    def __init__(self, should_change: bool, value: Optional[UpdateActionType] = None) -> None:
        """Constructor."""
        self._should_change = should_change
        self._value = value

    @staticmethod
    def do_nothing() -> 'UpdateAction[UpdateActionType]':
        """An update action where nothing needs to happen."""
        return UpdateAction[UpdateActionType](should_change=False)

    @staticmethod
    def change_to(value: UpdateActionType) -> 'UpdateAction[UpdateActionType]':
        """An update action where the value needs to be changed to a new value."""
        return UpdateAction[UpdateActionType](should_change=True, value=value)

    def or_else(self, value_if_should_not_change: UpdateActionType) -> UpdateActionType:
        """Return the value of the action if it should change or the argument if it should not."""
        if self._should_change:
            return typing.cast(UpdateActionType, self._value)
        else:
            return value_if_should_not_change

    @property
    def should_change(self) -> bool:
        """Whether the value should change or not."""
        return self._should_change

    @property
    def value(self) -> UpdateActionType:
        """Return the value if it exists."""
        if not self._should_change:
            raise Exception("Trying to get the value when it's not there")
        return typing.cast(UpdateActionType, self._value)
