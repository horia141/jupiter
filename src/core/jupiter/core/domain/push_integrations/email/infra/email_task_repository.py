"""A repository of Email tasks."""
import abc

from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class EmailTaskRepository(LeafEntityRepository[EmailTask], abc.ABC):
    """A repository of email tasks."""
