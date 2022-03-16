"""Create a person."""
import logging
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.persons.infra.person_notion_manager import PersonNotionManager
from jupiter.domain.persons.notion_person import NotionPerson
from jupiter.domain.persons.person import Person
from jupiter.domain.persons.person_birthday import PersonBirthday
from jupiter.domain.persons.person_name import PersonName
from jupiter.domain.persons.person_relationship import PersonRelationship
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class PersonCreateUseCase(AppMutationUseCase['PersonCreateUseCase.Args', None]):
    """The command for creating a person."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        name: PersonName
        relationship: PersonRelationship
        catch_up_period: Optional[RecurringTaskPeriod]
        catch_up_eisen: Optional[Eisen]
        catch_up_difficulty: Optional[Difficulty]
        catch_up_actionable_from_day: Optional[RecurringTaskDueAtDay]
        catch_up_actionable_from_month: Optional[RecurringTaskDueAtMonth]
        catch_up_due_at_time: Optional[RecurringTaskDueAtTime]
        catch_up_due_at_day: Optional[RecurringTaskDueAtDay]
        catch_up_due_at_month: Optional[RecurringTaskDueAtMonth]
        birthday: Optional[PersonBirthday]

    _person_notion_manager: Final[PersonNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            person_notion_manager: PersonNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._person_notion_manager = person_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            person_collection = uow.person_collection_repository.load_by_parent(workspace.ref_id)

            catch_up_params = None
            if args.catch_up_period is not None:
                catch_up_params = RecurringTaskGenParams(
                    period=args.catch_up_period,
                    eisen=args.catch_up_eisen if args.catch_up_eisen else Eisen.REGULAR,
                    difficulty=args.catch_up_difficulty,
                    actionable_from_day=args.catch_up_actionable_from_day,
                    actionable_from_month=args.catch_up_actionable_from_month,
                    due_at_time=args.catch_up_due_at_time,
                    due_at_day=args.catch_up_due_at_day,
                    due_at_month=args.catch_up_due_at_month)

            person = \
                Person.new_person(
                    person_collection_ref_id=person_collection.ref_id, name=args.name, relationship=args.relationship,
                    catch_up_params=catch_up_params, birthday=args.birthday, source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            person = uow.person_repository.create(person)

        notion_person = NotionPerson.new_notion_entity(person, None)
        self._person_notion_manager.upsert_leaf(person_collection.ref_id, notion_person, None)
