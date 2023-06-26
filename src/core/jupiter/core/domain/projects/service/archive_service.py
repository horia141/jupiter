"""Shared logic for archiving a project."""
from typing import Final

from jupiter.core.domain.big_plans.service.archive_service import BigPlanArchiveService
from jupiter.core.domain.chores.service.archive_service import ChoreArchiveService
from jupiter.core.domain.habits.service.archive_service import HabitArchiveService
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.projects.errors import ProjectInSignificantUseError
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ContextProgressReporter
from jupiter.core.utils.time_provider import TimeProvider


class ProjectArchiveService:
    """Shared logic for archiving a project."""

    _source: Final[EventSource]
    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        source: EventSource,
        time_provider: TimeProvider,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        self._source = source
        self._time_provider = time_provider
        self._storage_engine = storage_engine

    async def do_it(
        self,
        progress_reporter: ContextProgressReporter,
        workspace: Workspace,
        ref_id: EntityId,
    ) -> None:
        """Archive the project."""
        async with self._storage_engine.get_unit_of_work() as uow:
            project = await uow.project_repository.load_by_id(
                ref_id, allow_archived=False
            )

            # test it's not the workspace default project nor a metric collection project nor a person catchup one
            if workspace.default_project_ref_id == project.ref_id:
                raise ProjectInSignificantUseError(
                    "The project is being used as the workspace default one"
                )
            metric_collection = await uow.metric_collection_repository.load_by_parent(
                workspace.ref_id
            )
            if metric_collection.collection_project_ref_id == project.ref_id:
                raise ProjectInSignificantUseError(
                    "The project is being used as the metric collection default one"
                )
            person_collection = await uow.person_collection_repository.load_by_parent(
                workspace.ref_id
            )
            if person_collection.catch_up_project_ref_id == project.ref_id:
                raise ProjectInSignificantUseError(
                    "The project is being used as the person catch up one"
                )

            # archive inbox tasks
            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id
                )
            )
            inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=False,
                filter_project_ref_ids=[project.ref_id],
            )
            inbox_task_archive_service = InboxTaskArchiveService(
                self._source, self._time_provider, self._storage_engine
            )
            for it in inbox_tasks:
                await inbox_task_archive_service.do_it(progress_reporter, it)

            # archive chores
            chore_collection = await uow.chore_collection_repository.load_by_parent(
                workspace.ref_id
            )
            chores = await uow.chore_repository.find_all_with_filters(
                parent_ref_id=chore_collection.ref_id,
                allow_archived=False,
                filter_project_ref_ids=[project.ref_id],
            )
            chore_archive_service = ChoreArchiveService(
                self._source, self._time_provider, self._storage_engine
            )
            for chore in chores:
                await chore_archive_service.do_it(progress_reporter, chore)

            # archive habits
            habit_collection = await uow.habit_collection_repository.load_by_parent(
                workspace.ref_id
            )
            habits = await uow.habit_repository.find_all_with_filters(
                parent_ref_id=habit_collection.ref_id,
                allow_archived=False,
                filter_project_ref_ids=[project.ref_id],
            )
            habit_archive_service = HabitArchiveService(
                self._source, self._time_provider, self._storage_engine
            )
            for habit in habits:
                await habit_archive_service.do_it(progress_reporter, habit)

            # archive big plans
            big_plan_collection = await uow.habit_collection_repository.load_by_parent(
                workspace.ref_id
            )
            big_plans = await uow.big_plan_repository.find_all_with_filters(
                parent_ref_id=big_plan_collection.ref_id,
                allow_archived=False,
                filter_project_ref_ids=[project.ref_id],
            )
            big_plan_archive_service = BigPlanArchiveService(
                self._source, self._time_provider, self._storage_engine
            )
            for big_plan in big_plans:
                await big_plan_archive_service.do_it(progress_reporter, big_plan)

            # archive project
            async with progress_reporter.start_archiving_entity(
                "project", project.ref_id, str(project.name)
            ) as entity_reporter:
                project = project.mark_archived(
                    self._source, self._time_provider.get_current_time()
                )
                await uow.project_repository.save(project)
                await entity_reporter.mark_local_change()