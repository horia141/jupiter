import coloredlogs
from sqlalchemy import create_engine

from alembic import context

try:
    from jupiter.utils.global_properties import build_global_properties
except ModuleNotFoundError:
    from jupiter.utils.global_properties import build_global_properties


coloredlogs.install(
    level='info',
    fmt='%(asctime)s %(name)-12s %(levelname)-6s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    global_properties = build_global_properties()
    context.configure(
        url=global_properties.sqlite_db_url,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'})

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    global_properties = build_global_properties()
    engine = create_engine(global_properties.sqlite_db_url)

    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=None)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
