"""Essential info about a big plan."""
from dataclasses import dataclass

from domain.entity_name import EntityName
from models.framework import EntityId


@dataclass()
class BigPlanEssentials:
    """Essential info about a big plan."""

    ref_id: EntityId
    name: EntityName
