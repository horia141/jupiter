"""Use case for creating a schedule stream from an external iCal."""
from icalendar import Calendar
from jupiter.core.domain.concept.schedule.schedule_domain import ScheduleDomain
from jupiter.core.domain.concept.schedule.schedule_stream import ScheduleStream
from jupiter.core.domain.concept.schedule.schedule_stream_color import ScheduleStreamColor
from jupiter.core.domain.concept.schedule.schedule_stream_name import ScheduleStreamName
from jupiter.core.domain.core.url import URL
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_creator import generic_creator
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.realm import RealmDecodingError
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseResultBase, use_case_args, use_case_result
from jupiter.core.use_cases.infra.use_cases import AppLoggedInMutationUseCaseContext, AppTransactionalLoggedInMutationUseCase, mutation_use_case
import requests


@use_case_args
class ScheduleStreamCreateForExternalIcalArgs(UseCaseArgsBase):
    """Args."""

    source_ical_url: URL


@use_case_result
class ScheduleStreamCreateForExternalIcalResult(UseCaseResultBase):
    """Result."""

    new_schedule_stream: ScheduleStream


@mutation_use_case(WorkspaceFeature.SCHEDULE)
class ScheduleStreamCreateForExternalIcalUseCase(
    AppTransactionalLoggedInMutationUseCase[
        ScheduleStreamCreateForExternalIcalArgs, ScheduleStreamCreateForExternalIcalResult
    ]
):
    """Use case for creating a schedule stream from an external iCal."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ScheduleStreamCreateForExternalIcalArgs,
    ) -> ScheduleStreamCreateForExternalIcalResult:
        """Perform the transactional mutation."""
        workspace = context.workspace
        schedule_domain = await uow.get_for(ScheduleDomain).load_by_parent(
            workspace.ref_id
        )

        calendar_ical_response = requests.get(args.source_ical_url.the_url)
        if calendar_ical_response.status_code != 200:
            raise InputValidationError(f"Failed to fetch iCal from {args.source_ical_url} (error {calendar_ical_response.status_code})")
        calendar_ical = calendar_ical_response.text

        try:
            calendar = Calendar.from_ical(calendar_ical)
        except Exception as err:
            raise InputValidationError(f"Failed to parse iCal from {args.source_ical_url} ({err})")

        name = self._realm_codec_registry.db_decode(ScheduleStreamName, calendar.get("X-WR-CALNAME"))
        try:
            color = self._realm_codec_registry.db_decode(ScheduleStreamColor, calendar.get("COLOR"))
        except RealmDecodingError:
            color = ScheduleStreamColor.YELLOW

        schedule_stream = ScheduleStream.new_schedule_stream_from_external_ical(
            context.domain_context,
            schedule_domain_ref_id=schedule_domain.ref_id,
            name=name,
            color=color,
            source_ical_url=args.source_ical_url
        )
        schedule_stream = await generic_creator(uow, progress_reporter, schedule_stream)
        return ScheduleStreamCreateForExternalIcalResult(new_schedule_stream=schedule_stream)