"""The service class for dealing with projects."""
import logging
from dataclasses import dataclass
from typing import Final, Iterable, Optional

from models.basic import ProjectKey, BasicValidator, SyncPrefer, EntityId
from models.errors import ModelValidationError
from remote.notion.common import NotionPageLink
from remote.notion.projects_manager import NotionProjectsManager
from repository.projects import ProjectsRepository, ProjectRow
from service.errors import ServiceValidationError

LOGGER = logging.getLogger(__name__)


@dataclass()
class ProjectWithPage:
    """A project."""

    ref_id: EntityId
    key: ProjectKey
    name: str
    notion_page_link: NotionPageLink


@dataclass()
class Project:
    """A project."""

    ref_id: EntityId
    key: ProjectKey
    name: str


class ProjectsService:
    """The service class for dealing with projects."""

    _basic_validator: Final[BasicValidator]
    _repository: Final[ProjectsRepository]
    _notion_manager: Final[NotionProjectsManager]

    def __init__(
            self, basic_validator: BasicValidator, repository: ProjectsRepository,
            notion_manager: NotionProjectsManager) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._repository = repository
        self._notion_manager = notion_manager

    def upsert_root_notion_structure(self, parent_page: NotionPageLink) -> None:
        """Create the root page where all the projects will be placed."""
        self._notion_manager.upsert_root_page(parent_page)

    def create_project(self, key: ProjectKey, name: str) -> ProjectWithPage:
        """Create a project."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        new_project_row = self._repository.create_project(
            key=key,
            name=name,
            archived=False)
        LOGGER.info("Applied local changes")

        new_project_page = self._notion_manager.upsert_project(ref_id=new_project_row.ref_id, name=name)
        LOGGER.info("Applied Notion changes")

        return ProjectWithPage(
            ref_id=new_project_row.ref_id,
            key=new_project_row.key,
            name=new_project_row.name,
            notion_page_link=NotionPageLink(page_id=new_project_page.notion_id))

    def upsert_project_structure(self, ref_id: EntityId) -> ProjectWithPage:
        """Upsert the structure around a project."""
        project_row = self._repository.load_project(ref_id)
        project_page = self._notion_manager.upsert_project(ref_id, project_row.name)

        return ProjectWithPage(
            ref_id=project_row.ref_id,
            key=project_row.key,
            name=project_row.name,
            notion_page_link=NotionPageLink(page_id=project_page.notion_id))

    def archive_project(self, ref_id: EntityId) -> Project:
        """Archive a project."""
        project_row = self._repository.archive_project(ref_id)
        LOGGER.info("Applied local changes")
        self._notion_manager.archive_project(project_row.ref_id)
        LOGGER.info("Applied Notion changes")
        return self._row_to_entity(project_row)

    def set_project_name(self, ref_id: EntityId, name: str) -> Project:
        """Change the name of a project."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        project_row = self._repository.load_project(ref_id)
        project_row.name = name
        self._repository.update_project(project_row)
        LOGGER.info("Modified local project")

        project_page = self._notion_manager.load_project(project_row.ref_id)
        project_page.name = name
        self._notion_manager.save_project(project_page)
        LOGGER.info("Applied Notion changes")

        return self._row_to_entity(project_row)

    def load_project_by_ref_id(self, ref_id: EntityId) -> Project:
        """Retrieve a particular project, by key."""
        project_row = self._repository.load_project(ref_id)
        return self._row_to_entity(project_row)

    def load_project_by_key(self, key: ProjectKey) -> Project:
        """Retrieve a particular project, by key."""
        project_row = self._repository.load_project_by_key(key)
        return self._row_to_entity(project_row)

    def load_all_projects(
            self, allow_archived: bool = False,
            filter_keys: Optional[Iterable[ProjectKey]] = None) -> Iterable[Project]:
        """Retrieve all projects."""
        project_rows = self._repository.find_all_projects(allow_archived=allow_archived, filter_keys=filter_keys)
        return [self._row_to_entity(p) for p in project_rows]

    def sync_projects(self, ref_id: EntityId, sync_prefer: SyncPrefer) -> Project:
        """Synchronise projects between Notion and local storage."""
        project_row = self._repository.load_project(ref_id, allow_archived=True)
        project_page = self._notion_manager.load_project(project_row.ref_id)

        if sync_prefer == SyncPrefer.LOCAL:
            project_page.name = project_row.name
            self._notion_manager.save_project(project_page)
            LOGGER.info("Applied changes to Notion")
        elif sync_prefer == SyncPrefer.NOTION:
            project_row.name = project_page.name
            self._repository.update_project(project_row)
            LOGGER.info("Applied local change")
        else:
            raise Exception(f"Invalid preference {sync_prefer}")

        return self._row_to_entity(project_row)

    @staticmethod
    def _row_to_entity(row: ProjectRow) -> Project:
        return Project(
            ref_id=row.ref_id,
            key=row.key,
            name=row.name)
