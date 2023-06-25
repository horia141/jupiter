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

    def __repr__(self) -> str:
        """The representation of this action."""
        if self._should_change:
            return f"UpdateAction.change_to({repr(self._value)})"
        else:
            return "UpdateAction.do_nothing()"

    @property
    def should_change(self) -> bool:
        """Whether this represents an action for change or not."""
        return self._should_change

    @classmethod
    def __get_validators__(cls) -> typing.Iterable[typing.Callable[..., typing.Any]]:
        """All the pydantic validators to apply here."""
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: typing.Dict[str, typing.Any]) -> None:
        """Modify the OpenAPI schema for this entry."""
        # Time for sourcery.
        old_ref = field_schema["allOf"][0]
        del field_schema["allOf"]

        field_schema["type"] = "object"
        field_schema["required"] = ["should_change"]
        field_schema["properties"] = {
            "should_change": {"title": "Should Change", "type": "boolean"},
            "value": old_ref,
        }

    @classmethod
    def validate(
        cls,
        the_v: typing.Any,
        field: ModelField,
    ) -> "UpdateAction[UpdateActionT]":
        """Attempt to validate this and its sub-object, useful for pydantic."""
        if not field.sub_fields:
            # Generic parameters were not provided so we don't try to validate
            # them and just return the value as is
            return typing.cast(UpdateAction[UpdateActionT], the_v)

        if isinstance(the_v, UpdateAction):
            aged_f = field.sub_fields[0]
            if not the_v.should_change:
                return the_v.do_nothing()
            # Here we don't need the validated value, but we want the errors
            valid_value, error = aged_f.validate(the_v.just_the_value, {}, loc="value")
            if error:
                raise Exception(error)
            return the_v.change_to(valid_value)
        elif isinstance(the_v, dict):
            should_change = the_v.get("should_change")
            if should_change is None:
                raise ValueError("Missing change info for update action")
            if not isinstance(should_change, bool):
                raise ValueError(
                    f"Change info has type {should_change.__class__.__name__}",
                )
            if not should_change:
                return UpdateAction.do_nothing()
            if "value" not in the_v:
                if not field.sub_fields[0].required:
                    return UpdateAction.change_to(field.sub_fields[0].default)
                else:
                    raise ValueError("Missing value for update action")
            value = the_v["value"]
            aged_f = field.sub_fields[0]
            valid_value, errors = aged_f.validate(value, {}, loc="value")
            if errors:
                raise ValidationError([errors], aged_f.type_.__class__)
            return UpdateAction.change_to(typing.cast(UpdateActionT, valid_value))
        else:
            raise ValueError(f"Something's really funky {the_v.__class__.__name__}")
