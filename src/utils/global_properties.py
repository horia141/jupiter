"""Command-level properties."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import cast, Optional

import dotenv

from domain.common.timezone import Timezone


@dataclass(frozen=True)
class GlobalProperties:
    """Command-level properties."""

    description: str
    version: str
    timezone: Timezone
    docs_init_workspace_url: str
    docs_update_expired_token_url: str
    docs_fix_data_inconsistencies_url: str
    sqlite_db_url: str
    alembic_ini_path: Path
    alembic_migrations_path: Path


def build_global_properties(timezone: Optional[Timezone] = None) -> GlobalProperties:
    """Build the global properties from the environment."""
    config_path = Path(os.path.realpath(Path(os.path.realpath(__file__)).parent / ".." / ".." / "Config"))

    if not config_path.exists():
        raise Exception("Critical error - missing Config file")

    dotenv.load_dotenv(dotenv_path=config_path, verbose=True)

    description = cast(str, os.getenv("DESCRIPTION"))
    version = cast(str, os.getenv("VERSION"))
    docs_init_workspace_url = cast(str, os.getenv("DOCS_INIT_WORKSPACE_URL"))
    docs_update_expired_token_url = cast(str, os.getenv("DOCS_UPDATE_EXPIRED_TOKEN_URL"))
    docs_fix_data_inconsistencies_url = cast(str, os.getenv("DOCS_FIX_DATA_INCONSISTENCIES_URL"))
    sqlite_db_url = cast(str, os.getenv("SQLITE_DB_URL"))
    alembic_ini_path = cast(str, os.getenv("ALEMBIC_INI_PATH"))
    alembic_migrations_path = cast(str, os.getenv("ALEMBIC_MIGRATIONS_PATH"))

    return GlobalProperties(
        description=description,
        version=version,
        timezone=timezone or Timezone.from_raw(os.getenv("TZ", "UTC")),
        docs_init_workspace_url=docs_init_workspace_url,
        docs_update_expired_token_url=docs_update_expired_token_url,
        docs_fix_data_inconsistencies_url=docs_fix_data_inconsistencies_url,
        sqlite_db_url=sqlite_db_url,
        alembic_ini_path=Path(alembic_ini_path),
        alembic_migrations_path=Path(alembic_migrations_path))
