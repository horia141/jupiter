"""A suggested date for an inbox task."""

from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.value import CompositeValue, value


@value
class SuggestedDate(CompositeValue):
    """A suggested date for an inbox task."""

    date: ADate
    description: str
