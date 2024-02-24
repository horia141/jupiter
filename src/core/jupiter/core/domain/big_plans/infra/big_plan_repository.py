"""A repository of big plans."""
import abc
from typing import Iterable, List, Optional

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class BigPlanRepository(LeafEntityRepository[BigPlan], abc.ABC):
    """A repository of big plans."""
