"""A thing is some data carrying domain or generic object."""
from datetime import date, datetime
from typing import TypeGuard, get_origin

from jupiter.core.framework.concept import Concept
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.use_case_io import UseCaseArgsBase
from jupiter.core.framework.value import (
    AtomicValue,
    CompositeValue,
    EnumValue,
    SecretValue,
    Value,
)
from pendulum.date import Date
from pendulum.datetime import DateTime

Thing = Concept | Primitive | UseCaseArgsBase

ValueIsh = Value | Primitive


def is_value_ish_type(
    the_type: type[Thing],
) -> TypeGuard[type[ValueIsh]]:
    return (
        the_type in (type(None), bool, int, float, str, date, datetime, Date, DateTime)
        or isinstance(the_type, type)
        and get_origin(the_type) is None
        and issubclass(the_type, (AtomicValue, CompositeValue, EnumValue, SecretValue))
    )
