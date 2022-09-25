"""A temporary migrator."""
import logging

from rich.logging import RichHandler

LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Application main function."""
    logging.basicConfig(
        level="info",
        format="%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            RichHandler(
                rich_tracebacks=True, markup=True, log_time_format="%Y-%m-%d %H:%M:%S"
            )
        ],
    )
    # time_provider = TimeProvider()

    # global_properties = build_global_properties()

    # yaml_repo = YamlInboxTaskRepository(time_provider)
    # storage_engine = \
    #     SqliteDomainStorageEngine(
    #         time_provider,
    #         SqliteDomainStorageEngine.Config(
    #             global_properties.sqlite_db_url, global_properties.alembic_ini_path,
    #             global_properties.alembic_migrations_path))
    #
    # with storage_engine.get_unit_of_work() as uow:
    #     for entity in yaml_repo.find_all(allow_archived=True):
    #         uow.inbox_task_collection_repository.create(entity)

    # with storage_engine.get_unit_of_work() as uow:
    #     for collection in uow.inbox_task_collection_repository.find_all(allow_archived=True):
    #         for entity in yaml_repo.find_all(
    #               allow_archived=True, filter_inbox_task_collection_ref_ids=[collection.ref_id]):
    #             LOGGER.error(entity)
    #             uow.inbox_task_repository.create(collection, entity)

    # repository = YamlInboxTaskRepository(time_provider)
    # entities = repository.find_all(allow_archived=True)
    # repository.dump_all(entities)


if __name__ == "__main__":
    main()
