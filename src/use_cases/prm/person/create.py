"""Create a person."""
import logging
from dataclasses import dataclass
from typing import Final, Optional, List

from domain.difficulty import Difficulty
from domain.eisen import Eisen
from domain.entity_name import EntityName
from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.notion_person import NotionPerson
from domain.prm.person import Person
from domain.prm.person_birthday import PersonBirthday
from domain.prm.person_relationship import PersonRelationship
from domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from domain.recurring_task_gen_params import RecurringTaskGenParams
from domain.recurring_task_period import RecurringTaskPeriod
from models.framework import Command
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class PersonCreateCommand(Command['PersonCreateCommand.Args', None]):
    """The command for creating a person."""

    @dataclass()
    class Args:
        """Args."""
        name: EntityName
        relationship: PersonRelationship
        catch_up_period: Optional[RecurringTaskPeriod]
        catch_up_eisen: List[Eisen]
        catch_up_difficulty: Optional[Difficulty]
        catch_up_actionable_from_day: Optional[RecurringTaskDueAtDay]
        catch_up_actionable_from_month: Optional[RecurringTaskDueAtMonth]
        catch_up_due_at_time: Optional[RecurringTaskDueAtTime]
        catch_up_due_at_day: Optional[RecurringTaskDueAtDay]
        catch_up_due_at_month: Optional[RecurringTaskDueAtMonth]
        birthday: Optional[PersonBirthday]

    _time_provider: Final[TimeProvider]
    _prm_engine: Final[PrmEngine]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self, time_provider: TimeProvider, prm_engine: PrmEngine,
            prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._prm_engine = prm_engine
        self._prm_notion_manager = prm_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        catch_up_params = None
        if args.catch_up_period is not None:
            with self._prm_engine.get_unit_of_work() as uow:
                prm_database = uow.prm_database_repository.find()
                project_ref_id = prm_database.catch_up_project_ref_id
            catch_up_params = RecurringTaskGenParams(
                project_ref_id=project_ref_id,
                period=args.catch_up_period,
                eisen=args.catch_up_eisen,
                difficulty=args.catch_up_difficulty,
                actionable_from_day=args.catch_up_actionable_from_day,
                actionable_from_month=args.catch_up_actionable_from_month,
                due_at_time=args.catch_up_due_at_time,
                due_at_day=args.catch_up_due_at_day,
                due_at_month=args.catch_up_due_at_month)

        person = Person.new_person(
            name=args.name, relationship=args.relationship, catch_up_params=catch_up_params,
            birthday=args.birthday, created_time=self._time_provider.get_current_time())
        with self._prm_engine.get_unit_of_work() as uow:
            person = uow.person_repository.create(person)
        notion_person = NotionPerson.new_notion_row(person)
        self._prm_notion_manager.upsert_person(notion_person)
