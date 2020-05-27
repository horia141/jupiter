"""The service class for dealing with projects."""
import logging
from dataclasses import dataclass
from typing import Final, Iterable, Optional

from models.basic import ProjectKey, BasicValidator, ModelValidationError, SyncPrefer
from remote.notion.common import NotionPageLink
from remote.notion.projects import ProjectsCollection, ProjectScreen
from repository.projects import ProjectsRepository, Project
from service.errors import ServiceValidationError

LOGGER = logging.getLogger(__name__)


@dataclass()
class CreateProjectResponse:
    """Response object for the create_project method."""

    project: Project
    project_screen: ProjectScreen

    @property
    def page(self) -> NotionPageLink:
        """The screen as a page."""
        return NotionPageLink(self.project_screen.notion_id)


class ProjectsService:
    """The service class for dealing with projects."""

    _basic_validator: Final[BasicValidator]
    _repository: Final[ProjectsRepository]
    _collection: Final[ProjectsCollection]

    def __init__(
            self, basic_validator: BasicValidator, repository: ProjectsRepository,
            collection: ProjectsCollection) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._repository = repository
        self._collection = collection

    def create_project(self, key: ProjectKey, name: str, parent_page: NotionPageLink) -> CreateProjectResponse:
        """Create a project."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        new_project = self._repository.create_project(
            key=key,
            name=name,
            archived=False)
        LOGGER.info("Applied local changes")

        new_project_screen = self._collection.create_project(
            name=name,
            ref_id=new_project.ref_id,
            parent_page=parent_page)
        LOGGER.info("Applied Notion changes")

        return CreateProjectResponse(
            project=new_project,
            project_screen=new_project_screen)

    def archive_project(self, key: ProjectKey) -> None:
        """Archive a project."""
        removed_project = self._repository.remove_project_by_key(key)
        LOGGER.info("Applied local changes")
        self._collection.remove_project(removed_project.ref_id)

    def set_project_name(self, key: ProjectKey, name: str) -> None:
        """Change the name of a project."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        project = self._repository.load_project_by_key(key)
        project.name = name
        self._repository.save_project(project)
        LOGGER.info("Modified local project")

        project_screen = self._collection.load_project_by_id(project.ref_id)
        project_screen.name = name
        self._collection.save_project(project_screen)
        LOGGER.info("Applied Notion changes")

    def load_all_projects(
            self, show_archived: bool = False, filter_keys: Optional[Iterable[ProjectKey]] = None) -> Iterable[Project]:
        """Retrieve all projects."""
        return self._repository.list_all_projects(
            filter_archived=not show_archived, filter_keys=filter_keys)

    def load_project_by_key(self, key: ProjectKey) -> Project:
        """Retrieve a particular project, by key."""
        return self._repository.load_project_by_key(key)

    def sync_projects(self, key: ProjectKey, sync_prefer: SyncPrefer) -> None:
        """Synchronise projects between Notion and local storage."""
        project = self._repository.load_project_by_key(key)
        project_screen = self._collection.load_project_by_id(project.ref_id)

        if sync_prefer == SyncPrefer.LOCAL:
            project_screen.name = project.name
            self._collection.save_project(project_screen)
            LOGGER.info("Applied changes to Notion")
        elif sync_prefer == SyncPrefer.NOTION:
            project.name = project_screen.name
            self._repository.save_project(project)
            LOGGER.info("Applied local change")
        else:
            raise Exception(f"Invalid preference {sync_prefer}")
