"""The command for updating a vacation's properties."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.adate import ADate
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from jupiter.domain.vacations.vacation_name import VacationName
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
)
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider


class VacationUpdateUseCase(AppMutationUseCase["VacationUpdateUseCase.Args", None]):
    """The command for updating a vacation's properties."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        ref_id: EntityId
        name: UpdateAction[VacationName]
        start_date: UpdateAction[ADate]
        end_date: UpdateAction[ADate]

    _vacation_notion_manager: Final[VacationNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        notion_manager: VacationNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._vacation_notion_manager = notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            vacation_collection = uow.vacation_collection_repository.load_by_parent(
                workspace.ref_id
            )
            vacation = uow.vacation_repository.load_by_id(args.ref_id)

            vacation = vacation.update(
                name=args.name,
                start_date=args.start_date,
                end_date=args.end_date,
                source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time(),
            )

            uow.vacation_repository.save(vacation)

        notion_vacation = self._vacation_notion_manager.load_leaf(
            vacation_collection.ref_id, args.ref_id
        )
        notion_vacation = notion_vacation.join_with_entity(vacation, None)
        self._vacation_notion_manager.save_leaf(
            vacation_collection.ref_id, notion_vacation
        )
