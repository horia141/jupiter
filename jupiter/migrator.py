"""A temporary migrator."""
from jupiter.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.framework.event import EventSource
from jupiter.repository.sqlite.connection import SqliteConnection
from jupiter.repository.sqlite.domain.storage_engine import SqliteDomainStorageEngine
from jupiter.utils.global_properties import build_global_properties
from jupiter.utils.time_provider import TimeProvider


def main() -> None:
    """Application main function."""
    # logging.basicConfig(
    #     level="info",
    #     format="%(message)s",
    #     datefmt="%Y-%m-%d %H:%M:%S",
    #     handlers=[
    #         RichHandler(
    #             rich_tracebacks=True, markup=True, log_time_format="%Y-%m-%d %H:%M:%S"
    #         )
    #     ],
    # )
    time_provider = TimeProvider()

    global_properties = build_global_properties()

    sqlite_connection = SqliteConnection(
        SqliteConnection.Config(
            global_properties.sqlite_db_url,
            global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path,
        )
    )

    domain_storage_engine = SqliteDomainStorageEngine(sqlite_connection)

    with domain_storage_engine.get_unit_of_work() as uow:
        workspace = uow.workspace_repository.load()
        push_integration_group = uow.push_integration_group_repository.load_by_parent(
            workspace.ref_id
        )

        new_email_task_collection = EmailTaskCollection.new_email_task_collection(
            push_integration_group_ref_id=push_integration_group.ref_id,
            generation_project_ref_id=workspace.default_project_ref_id,
            source=EventSource.CLI,
            created_time=time_provider.get_current_time(),
        )
        new_email_task_collection = uow.email_task_collection_repository.create(
            new_email_task_collection
        )


if __name__ == "__main__":
    main()
