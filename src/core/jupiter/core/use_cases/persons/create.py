"""Create a person."""
from dataclasses import dataclass
from typing import Iterable, Optional

from jupiter.core.domain.difficulty import Difficulty
from jupiter.core.domain.eisen import Eisen
from jupiter.core.domain.features import Feature
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.persons.person_birthday import PersonBirthday
from jupiter.core.domain.persons.person_name import PersonName
from jupiter.core.domain.persons.person_relationship import PersonRelationship
from jupiter.core.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class PersonCreateArgs(UseCaseArgsBase):
    """Person create args.."""

    name: PersonName
    relationship: PersonRelationship
    catch_up_period: Optional[RecurringTaskPeriod] = None
    catch_up_eisen: Optional[Eisen] = None
    catch_up_difficulty: Optional[Difficulty] = None
    catch_up_actionable_from_day: Optional[RecurringTaskDueAtDay] = None
    catch_up_actionable_from_month: Optional[RecurringTaskDueAtMonth] = None
    catch_up_due_at_time: Optional[RecurringTaskDueAtTime] = None
    catch_up_due_at_day: Optional[RecurringTaskDueAtDay] = None
    catch_up_due_at_month: Optional[RecurringTaskDueAtMonth] = None
    birthday: Optional[PersonBirthday] = None


@dataclass
class PersonCreateResult(UseCaseResultBase):
    """Person create result."""

    new_person: Person


class PersonCreateUseCase(
    AppLoggedInMutationUseCase[PersonCreateArgs, PersonCreateResult]
):
    """The command for creating a person."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.PERSONS

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: PersonCreateArgs,
    ) -> PersonCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            person_collection = await uow.person_collection_repository.load_by_parent(
                workspace.ref_id,
            )

            catch_up_params = None
            if args.catch_up_period is not None:
                catch_up_params = RecurringTaskGenParams(
                    period=args.catch_up_period,
                    eisen=args.catch_up_eisen,
                    difficulty=args.catch_up_difficulty,
                    actionable_from_day=args.catch_up_actionable_from_day,
                    actionable_from_month=args.catch_up_actionable_from_month,
                    due_at_time=args.catch_up_due_at_time,
                    due_at_day=args.catch_up_due_at_day,
                    due_at_month=args.catch_up_due_at_month,
                )

            new_person = Person.new_person(
                person_collection_ref_id=person_collection.ref_id,
                name=args.name,
                relationship=args.relationship,
                catch_up_params=catch_up_params,
                birthday=args.birthday,
                source=EventSource.CLI,
                created_time=self._time_provider.get_current_time(),
            )
            new_person = await uow.person_repository.create(new_person)
            await progress_reporter.mark_created(new_person)

        return PersonCreateResult(new_person=new_person)
