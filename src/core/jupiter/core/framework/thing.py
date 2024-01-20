"""A thing is some data carrying domain or generic object."""
from jupiter.core.framework.concept import Concept
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import Value

Thing = Concept | Primitive

ValueIsh = Value | Primitive
