"""UseCase-level properties."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Union, cast

import dotenv
from jupiter.core.domain.timezone import Timezone
from jupiter.core.framework.env import Env
from jupiter.core.framework.secure import secure_fn


@dataclass
class GlobalProperties:
    """UseCase-level properties."""

    env: Env
    description: str
    version: str
    timezone: Timezone
    docs_init_workspace_url: str
    session_info_path: Path
    sqlite_db_url: str
    alembic_ini_path: Path
    alembic_migrations_path: Path
    auth_token_secret: str

    @property
    def sync_sqlite_db_url(self) -> str:
        """A safe sync version of the Sqlite DB url."""
        # Bit of implicit knowledge here.
        return self.sqlite_db_url.replace("sqlite+aiosqlite", "sqlite+pysqlite")


@secure_fn
def build_global_properties() -> GlobalProperties:
    """Build the global properties from the environment."""

    def find_up_the_dir_tree(partial_path: Union[str, Path]) -> Path:
        last_here = None
        right_here = Path(os.path.relpath(__file__)).parent
        while True:
            if last_here == right_here:
                raise Exception(f"Critical error - missing config file {partial_path}")
            config_file = right_here / partial_path
            if config_file.exists():
                return config_file
            last_here = right_here
            right_here = right_here.parent

    global_config_path = find_up_the_dir_tree("Config.global")
    project_config_path = find_up_the_dir_tree("Config.project")

    dotenv.load_dotenv(dotenv_path=global_config_path, verbose=True)
    dotenv.load_dotenv(dotenv_path=project_config_path, verbose=True)

    env = Env(cast(str, os.getenv("ENV")))
    description = cast(str, os.getenv("DESCRIPTION"))
    version = cast(str, os.getenv("VERSION"))
    docs_init_workspace_url = cast(str, os.getenv("DOCS_INIT_WORKSPACE_URL"))
    timezone = "Europe/Bucharest"
    # timezone = datetime.datetime.now().astimezone().tzinfo
    session_info_path = Path(cast(str, os.getenv("SESSION_INFO_PATH")))
    sqlite_db_url = cast(str, os.getenv("SQLITE_DB_URL"))
    alembic_ini_path = Path(cast(str, os.getenv("ALEMBIC_INI_PATH")))
    alembic_migrations_path = Path(cast(str, os.getenv("ALEMBIC_MIGRATIONS_PATH")))
    auth_token_secret = cast(str, os.getenv("AUTH_TOKEN_SECRET"))

    if not alembic_ini_path.is_absolute():
        alembic_ini_path = find_up_the_dir_tree(alembic_ini_path)
    if not alembic_migrations_path.is_absolute():
        alembic_migrations_path = find_up_the_dir_tree(alembic_migrations_path)

    return GlobalProperties(
        env=env,
        description=description,
        version=version,
        timezone=Timezone.from_raw(str(timezone)),
        docs_init_workspace_url=docs_init_workspace_url,
        session_info_path=session_info_path,
        sqlite_db_url=sqlite_db_url,
        alembic_ini_path=alembic_ini_path,
        alembic_migrations_path=alembic_migrations_path,
        auth_token_secret=auth_token_secret,
    )
