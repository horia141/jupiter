"""Command-level properties."""
from dataclasses import dataclass

from pendulum.tz.timezone import Timezone


@dataclass(frozen=True)
class GlobalProperties:
    """Command-level properties."""

    description: str
    version: str
    timezone: Timezone
    docs_init_workspace_url: str
    docs_update_expired_token_url: str
    docs_fix_data_inconsistencies_url: str
