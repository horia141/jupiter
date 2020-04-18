"""Repository for projects."""

import os.path
import logging
from typing import Any, Dict, ClassVar, Iterator, List, NewType, Optional, Sequence, Tuple

import jsonschema as js
import yaml

from repository.common import RefId, RepositoryError


LOGGER = logging.getLogger(__name__)


ProjectKey = NewType("ProjectKey", str)


class Project:
    """A project."""

    _ref_id: RefId
    _key: ProjectKey
    _name: str

    def __init__(self, ref_id: RefId, key: ProjectKey, name: str) -> None:
        """Constructor."""
        self._ref_id = ref_id
        self._key = key
        self._name = name

    def set_name(self, name: str) -> None:
        """Set the name of a project."""
        self._name = name

    @property
    def ref_id(self) -> RefId:
        """The id of a project."""
        return self._ref_id

    @property
    def key(self) -> ProjectKey:
        """The key of a project."""
        return self._key

    @property
    def name(self) -> str:
        """The name of a project."""
        return self._name


class ProjectsRepository:
    """A repository for projects."""

    _PROJECTS_FILE_PATH: ClassVar[str] = "/data/projects.yaml"

    _PROJECTS_SCHEMA: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            "next_idx": {"type": "number"},
            "entries": {
                "type": "array",
                "item": {
                    "type": "object",
                    "properties": {
                        "ref_id": {"type": "string"},
                        "key": {"type": "string"},
                        "name": {"type": "string"}
                    }
                }
            }
        }
    }

    _validator: Any

    def __init__(self) -> None:
        """Constructor."""
        custom_type_checker = js.Draft6Validator.TYPE_CHECKER

        self._validator = js.validators.extend(js.Draft6Validator, type_checker=custom_type_checker)

    def initialize(self) -> None:
        """Initialise this repository."""
        if os.path.exists(ProjectsRepository._PROJECTS_FILE_PATH):
            return
        self._bulk_save_projects((0, []))

    def create_project(self, key: ProjectKey, name: str) -> Project:
        """Create a project."""
        projects_next_idx, projects = self._bulk_load_projects()

        if self._find_project_by_key(key, projects):
            raise RepositoryError(f"Project with key='{key}' already exists")

        new_project = Project(RefId(str(projects_next_idx)), key, name)

        projects_next_idx += 1
        projects.append(new_project)

        self._bulk_save_projects((projects_next_idx, projects))

        return new_project

    def remove_project_by_key(self, key: ProjectKey) -> None:
        """Remove a particular project."""
        projects_next_idx, projects = self._bulk_load_projects()

        if not self._find_project_by_key(key, projects):
            raise RepositoryError(f"Project with key='{key}' does not exist")

        new_projects = filter(lambda p: p.key == key, projects)
        self._bulk_save_projects((projects_next_idx, new_projects))

    def list_all_projects(self) -> Iterator[Project]:
        """Retrieve all the projects defined."""
        _, projects = self._bulk_load_projects()
        return projects

    def load_project_by_key(self, key: ProjectKey) -> Project:
        """Retrieve a particular project by its key."""
        _, projects = self._bulk_load_projects()
        found_project = self._find_project_by_key(key, projects)
        if not found_project:
            raise RepositoryError(f"Project with key='{key}' does not exist")
        return found_project

    def save_project(self, new_project: Project) -> None:
        """Store a particular project with all new properties."""
        projects_next_idx, projects = self._bulk_load_projects()

        if not self._find_project_by_key(new_project.key, projects):
            raise RepositoryError(f"Project with key='{new_project.key}' does not exist")

        new_projects = [(p if p.ref_id != new_project.ref_id else new_project) for p in projects]
        self._bulk_save_projects((projects_next_idx, new_projects))

    def _bulk_load_projects(self) -> Tuple[int, List[Project]]:
        try:
            with open(ProjectsRepository._PROJECTS_FILE_PATH, "r") as projects_file:
                projects_ser = yaml.safe_load(projects_file)
                LOGGER.info("Loaded projects data")

                self._validator(ProjectsRepository._PROJECTS_SCHEMA).validate(projects_ser)
                LOGGER.info("Checked projects structure")

                projects_next_idx = projects_ser["next_idx"]
                projects = \
                    [Project(RefId(p["ref_id"]), ProjectKey(p["key"]), p["name"])
                     for p in projects_ser["entries"]]

                return projects_next_idx, projects
        except (IOError, yaml.YAMLError, js.ValidationError) as error:
            raise RepositoryError from error

    def _bulk_save_projects(self, bulk_data: Tuple[int, Iterator[Project]]) -> None:
        try:
            with open(ProjectsRepository._PROJECTS_FILE_PATH, "w") as projects_file:
                projects_ser = {
                    "next_idx": bulk_data[0],
                    "entries": [{
                        "ref_id": p.ref_id,
                        "key": p.key,
                        "name": p.name
                    } for p in bulk_data[1]]
                }

                self._validator(ProjectsRepository._PROJECTS_SCHEMA).validate(projects_ser)
                LOGGER.info("Checked projects structure")

                yaml.dump(projects_ser, projects_file)
                LOGGER.info("Saved projects")
        except (IOError, yaml.YAMLError, js.ValidationError) as error:
            raise RepositoryError from error

    @staticmethod
    def _find_project_by_key(key: ProjectKey, projects: Sequence[Project]) -> Optional[Project]:
        try:
            return next(p for p in projects if p.key == key)
        except StopIteration:
            return None
