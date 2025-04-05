"""Row type infra."""

from typing import Any

from sqlalchemy.engine import Row

RowType = Row[Any]  # type: ignore
# None | float | int | str | datetime | JSONDictType]
