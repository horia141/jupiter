"""Create a person."""
import logging
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.prm.infra.prm_notion_manager import PrmNotionManager
from jupiter.domain.prm.notion_person import NotionPerson
from jupiter.domain.prm.person import Person
from jupiter.domain.prm.person_birthday import PersonBirthday
from jupiter.domain.prm.person_name import PersonName
from jupiter.domain.prm.person_relationship import PersonRelationship
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class PersonCreateUseCase(UseCase['PersonCreateUseCase.Args', None]):
    """The command for creating a person."""

    @dataclass()
    class Args:
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

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: StorageEngine,
            prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._prm_notion_manager = prm_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            catch_up_params = None
            if args.catch_up_period is not None:
                prm_database = uow.prm_database_repository.load()
                project_ref_id = prm_database.catch_up_project_ref_id
                catch_up_params = RecurringTaskGenParams(
                    project_ref_id=project_ref_id,
                    period=args.catch_up_period,
                    eisen=args.catch_up_eisen if args.catch_up_eisen else Eisen.REGULAR,
                    difficulty=args.catch_up_difficulty,
                    actionable_from_day=args.catch_up_actionable_from_day,
                    actionable_from_month=args.catch_up_actionable_from_month,
                    due_at_time=args.catch_up_due_at_time,
                    due_at_day=args.catch_up_due_at_day,
                    due_at_month=args.catch_up_due_at_month)

            person = Person.new_person(
                name=args.name, relationship=args.relationship, catch_up_params=catch_up_params,
                birthday=args.birthday, created_time=self._time_provider.get_current_time())
            person = uow.person_repository.create(person)

        notion_person = NotionPerson.new_notion_row(person, None)
        self._prm_notion_manager.upsert_person(notion_person)
