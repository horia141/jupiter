"""The NoOp implementation of the CRM."""

import logging

from jupiter.core.domain.concept.user.user import User
from jupiter.core.domain.crm import CRM

LOGGER = logging.getLogger(__name__)


class NoOpCRM(CRM):
    """The NoOp implementation of the CRM."""

    async def upsert_as_user(self, user: User) -> None:
        """Upsert a user in the CRM."""
        LOGGER.info("Upserting user %s in the CRM", user.email_address)
