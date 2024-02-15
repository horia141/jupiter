"""A thing is some data carrying domain or generic object."""

from jupiter.core.framework.concept import Concept
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseResultBase
from jupiter.core.framework.value import (
    Value,
)

Thing = Concept | Primitive | UseCaseArgsBase | UseCaseResultBase

ValueIsh = Value | Primitive
