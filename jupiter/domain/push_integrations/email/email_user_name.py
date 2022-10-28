"""An email user name."""
from dataclasses import dataclass

from jupiter.domain.entity_name import EntityName


@dataclass(frozen=True)
class EmailUserName(EntityName):
    """An email user name."""
