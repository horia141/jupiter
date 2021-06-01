"""Create a person."""
import logging
from dataclasses import dataclass
from typing import Final, Optional, List

from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.notion_person import NotionPerson
from domain.prm.person import Person
from domain.prm.person_birthday import PersonBirthday
from domain.prm.person_relationship import PersonRelationship
from domain.common.recurring_task_gen_params import RecurringTaskGenParams
from models.basic import RecurringTaskPeriod, Eisen, Difficulty
from models.framework import Command
from service.inbox_tasks import InboxTasksService
from service.workspaces import WorkspacesService
from utils.time_provider import TimeProvider


LOGGER = logging.getLogger(__name__)


class PersonCreateCommand(Command['PersonCreateCommand.Args', None]):
    """The command for creating a person."""

    @dataclass()
    class Args:
        """Args."""
        name: str
        relationship: PersonRelationship
        catch_up_period: Optional[RecurringTaskPeriod]
        catch_up_eisen: List[Eisen]
        catch_up_difficulty: Optional[Difficulty]
        catch_up_actionable_from_day: Optional[int]
        catch_up_actionable_from_month: Optional[int]
        catch_up_due_at_time: Optional[str]
        catch_up_due_at_day: Optional[int]
        catch_up_due_at_month: Optional[int]
        birthday: Optional[PersonBirthday]

    _time_provider: Final[TimeProvider]
    _engine: Final[PrmEngine]
    _notion_manager: Final[PrmNotionManager]
    _workspaces_service: Final[WorkspacesService]
    _inbox_tasks_service: Final[InboxTasksService]

    def __init__(
            self, time_provider: TimeProvider, engine: PrmEngine,
            notion_manager: PrmNotionManager, inbox_tasks_service: InboxTasksService,
            workspaces_service: WorkspacesService) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._engine = engine
        self._notion_manager = notion_manager
        self._workspaces_service = workspaces_service
        self._inbox_tasks_service = inbox_tasks_service

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        catch_up_params = None
        if args.catch_up_period is not None:
            with self._engine.get_unit_of_work() as uow:
                prm_database = uow.prm_database_repository.load()
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
        with self._engine.get_unit_of_work() as uow:
            person = uow.person_repository.create(person)
        notion_person = NotionPerson.new_notion_row(person)
        self._notion_manager.upsert_person(notion_person)
