"""A thing is some data carrying domain or generic object."""
from datetime import date, datetime
from typing import TypeGuard, get_origin

from jupiter.core.framework.concept import Concept
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseIOBase, UseCaseResultBase
from jupiter.core.framework.value import (
    AtomicValue,
    CompositeValue,
    EnumValue,
    SecretValue,
    Value,
)
from pendulum.date import Date
from pendulum.datetime import DateTime

Thing = Concept | Primitive | UseCaseArgsBase | UseCaseResultBase

ValueIsh = Value | Primitive
