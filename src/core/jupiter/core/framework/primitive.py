"""The primitive types."""

from datetime import date, datetime

from pendulum.date import Date
from pendulum.datetime import DateTime

Primitive = None | bool | int | float | str | date | datetime | Date | DateTime
