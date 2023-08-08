"""Archive a person."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class PersonArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class PersonArchiveUseCase(AppLoggedInMutationUseCase[PersonArchiveArgs, None]):
    """The command for archiving a person."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.PERSONS

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: PersonArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            person = await uow.person_repository.load_by_id(args.ref_id)

            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            all_inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                filter_sources=[
                    InboxTaskSource.PERSON_BIRTHDAY,
                    InboxTaskSource.PERSON_BIRTHDAY,
                ],
                filter_person_ref_ids=[person.ref_id],
            )

        inbox_task_archive_service = InboxTaskArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
            storage_engine=self._domain_storage_engine,
        )

        for inbox_task in all_inbox_tasks:
            await inbox_task_archive_service.do_it(progress_reporter, inbox_task)

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            person = person.mark_archived(
                EventSource.CLI,
                self._time_provider.get_current_time(),
            )
            await uow.person_repository.save(person)
            await progress_reporter.mark_updated(person)
