"""The SQLite implementation of the fast info repository."""

import json

from jupiter.core.domain.concept.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.concept.chores.chore_name import ChoreName
from jupiter.core.domain.concept.habits.habit_name import HabitName
from jupiter.core.domain.concept.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.concept.metrics.metric_name import MetricName
from jupiter.core.domain.concept.persons.person_name import PersonName
from jupiter.core.domain.concept.projects.project_name import ProjectName
from jupiter.core.domain.concept.schedule.schedule_source import ScheduleSource
from jupiter.core.domain.concept.schedule.schedule_stream_color import (
    ScheduleStreamColor,
)
from jupiter.core.domain.concept.schedule.schedule_stream_name import ScheduleStreamName
from jupiter.core.domain.concept.smart_lists.smart_list_name import SmartListName
from jupiter.core.domain.concept.vacations.vacation_name import VacationName
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.entity_icon import EntityIconDatabaseDecoder
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.fast_info_repository import (
    BigPlanSummary,
    ChoreSummary,
    FastInfoRepository,
    HabitSummary,
    InboxTaskSummary,
    JournalSummary,
    MetricSummary,
    PersonSummary,
    ProjectSummary,
    ScheduleStreamSummary,
    SmartListSummary,
    VacationSummary,
)
from jupiter.core.framework.base.entity_id import EntityId, EntityIdDatabaseDecoder
from jupiter.core.framework.base.entity_name import EntityNameDatabaseDecoder
from jupiter.core.impl.repository.sqlite.infra.repository import SqliteRepository
from sqlalchemy import text

_ENTITY_ID_DECODER = EntityIdDatabaseDecoder()
_SCHEDULE_STREAM_NAME_DECODER = EntityNameDatabaseDecoder(ScheduleStreamName)
_VACATION_NAME_DECODER = EntityNameDatabaseDecoder(VacationName)
_INBOX_TASK_NAME_DECODER = EntityNameDatabaseDecoder(InboxTaskName)
_PROJECT_NAME_DECODER = EntityNameDatabaseDecoder(ProjectName)
_HABIT_NAME_DECODER = EntityNameDatabaseDecoder(HabitName)
_CHORE_NAME_DECODER = EntityNameDatabaseDecoder(ChoreName)
_BIG_PLAN_NAME_DECODER = EntityNameDatabaseDecoder(BigPlanName)
_SMART_LIST_NAME_DECODER = EntityNameDatabaseDecoder(SmartListName)
_METRIC_NAME_DECODER = EntityNameDatabaseDecoder(MetricName)
_PERSON_NAME_DECODER = EntityNameDatabaseDecoder(PersonName)
_ENTITY_ICON_DECODER = EntityIconDatabaseDecoder()


class SqliteFastInfoRepository(SqliteRepository, FastInfoRepository):
    """The Sqlite based implementation for the fast info repository."""

    async def find_all_vacation_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[VacationSummary]:
        """Find all summaries about vacations."""
        query = """select ref_id, name from vacation where vacation_collection_ref_id = :parent_ref_id"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            (
                await self._connection.execute(
                    text(query), {"parent_ref_id": parent_ref_id.as_int()}
                )
            )
            .mappings()
            .all()
        )
        return [
            VacationSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_VACATION_NAME_DECODER.decode(row["name"]),
            )
            for row in result
        ]

    async def find_all_schedule_stream_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[ScheduleStreamSummary]:
        """Find all summaries about schedule streams."""
        query = """select ref_id, source, name, color from schedule_stream where schedule_domain_ref_id = :parent_ref_id"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            (
                await self._connection.execute(
                    text(query), {"parent_ref_id": parent_ref_id.as_int()}
                )
            )
            .mappings()
            .all()
        )
        return [
            ScheduleStreamSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                source=self._realm_codec_registry.db_decode(
                    ScheduleSource, row["source"]
                ),
                name=_SCHEDULE_STREAM_NAME_DECODER.decode(row["name"]),
                color=self._realm_codec_registry.db_decode(
                    ScheduleStreamColor, row["color"]
                ),
            )
            for row in result
        ]

    async def find_all_project_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[ProjectSummary]:
        """Find all summaries about projects."""
        query = """select ref_id, parent_project_ref_id, name, order_of_child_projects from project where project_collection_ref_id = :parent_ref_id"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            (
                await self._connection.execute(
                    text(query), {"parent_ref_id": parent_ref_id.as_int()}
                )
            )
            .mappings()
            .all()
        )
        return [
            ProjectSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                parent_project_ref_id=(
                    _ENTITY_ID_DECODER.decode(str(row["parent_project_ref_id"]))
                    if row["parent_project_ref_id"]
                    else None
                ),
                name=_PROJECT_NAME_DECODER.decode(row["name"]),
                order_of_child_projects=[
                    _ENTITY_ID_DECODER.decode(idx)
                    for idx in json.loads(row["order_of_child_projects"])
                ],
            )
            for row in result
        ]

    async def find_all_inbox_task_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[InboxTaskSummary]:
        """Find all summaries about inbox tasks."""
        query = """select ref_id, name from inbox_task where inbox_task_collection_ref_id = :parent_ref_id"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            (
                await self._connection.execute(
                    text(query), {"parent_ref_id": parent_ref_id.as_int()}
                )
            )
            .mappings()
            .all()
        )
        return [
            InboxTaskSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_INBOX_TASK_NAME_DECODER.decode(row["name"]),
            )
            for row in result
        ]

    async def find_all_journal_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
        filter_start_date: ADate,
        filter_end_date: ADate,
    ) -> list[JournalSummary]:
        """Find all summaries about journals."""
        query = """select ref_id, name from journal where journal_collection_ref_id = :parent_ref_id and right_now >= :filter_start_date and right_now <= :filter_end_date"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            (
                await self._connection.execute(
                    text(query),
                    {
                        "parent_ref_id": parent_ref_id.as_int(),
                        "filter_start_date": filter_start_date.the_date.to_date_string(),
                        "filter_end_date": filter_end_date.the_date.to_date_string(),
                    },
                )
            )
            .mappings()
            .all()
        )
        return [
            JournalSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_INBOX_TASK_NAME_DECODER.decode(row["name"]),
            )
            for row in result
        ]

    async def find_all_habit_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[HabitSummary]:
        """Find all summaries about habits."""
        query = """
            select
                ref_id,
                name,
                is_key,
                json_extract(gen_params, '$.period') as period,
                project_ref_id
            from habit
            where habit_collection_ref_id = :parent_ref_id
        """
        if not allow_archived:
            query += " and archived=0"
        result = (
            (
                await self._connection.execute(
                    text(query), {"parent_ref_id": parent_ref_id.as_int()}
                )
            )
            .mappings()
            .all()
        )
        return [
            HabitSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_HABIT_NAME_DECODER.decode(row["name"]),
                is_key=row["is_key"],
                period=self._realm_codec_registry.db_decode(
                    RecurringTaskPeriod, row["period"]
                ),
                project_ref_id=_ENTITY_ID_DECODER.decode(str(row["project_ref_id"])),
            )
            for row in result
        ]

    async def find_all_chore_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[ChoreSummary]:
        """Find all summaries about chores."""
        query = """select ref_id, name from chore where chore_collection_ref_id = :parent_ref_id"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            (
                await self._connection.execute(
                    text(query), {"parent_ref_id": parent_ref_id.as_int()}
                )
            )
            .mappings()
            .all()
        )
        return [
            ChoreSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_CHORE_NAME_DECODER.decode(row["name"]),
            )
            for row in result
        ]

    async def find_all_big_plan_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[BigPlanSummary]:
        """Find all summaries about big plans."""
        query = """select ref_id, name, project_ref_id from big_plan where big_plan_collection_ref_id = :parent_ref_id"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            (
                await self._connection.execute(
                    text(query), {"parent_ref_id": parent_ref_id.as_int()}
                )
            )
            .mappings()
            .all()
        )
        return [
            BigPlanSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_BIG_PLAN_NAME_DECODER.decode(row["name"]),
                project_ref_id=_ENTITY_ID_DECODER.decode(str(row["project_ref_id"])),
            )
            for row in result
        ]

    async def find_all_smart_list_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[SmartListSummary]:
        """Find all summaries about smart lists."""
        query = """select ref_id, name, icon from smart_list where smart_list_collection_ref_id = :parent_ref_id"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            (
                await self._connection.execute(
                    text(query), {"parent_ref_id": parent_ref_id.as_int()}
                )
            )
            .mappings()
            .all()
        )
        return [
            SmartListSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_SMART_LIST_NAME_DECODER.decode(row["name"]),
                icon=_ENTITY_ICON_DECODER.decode(row["icon"]) if row["icon"] else None,
            )
            for row in result
        ]

    async def find_all_metric_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[MetricSummary]:
        """Find all summaries about metrics."""
        query = """select ref_id, name, is_key, icon from metric where metric_collection_ref_id = :parent_ref_id"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            (
                await self._connection.execute(
                    text(query), {"parent_ref_id": parent_ref_id.as_int()}
                )
            )
            .mappings()
            .all()
        )
        return [
            MetricSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_METRIC_NAME_DECODER.decode(row["name"]),
                is_key=row["is_key"],
                icon=_ENTITY_ICON_DECODER.decode(row["icon"]) if row["icon"] else None,
            )
            for row in result
        ]

    async def find_all_person_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[PersonSummary]:
        """Find all summaries about persons."""
        query = """select ref_id, name from person where person_collection_ref_id = :parent_ref_id"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            (
                await self._connection.execute(
                    text(query), {"parent_ref_id": parent_ref_id.as_int()}
                )
            )
            .mappings()
            .all()
        )
        return [
            PersonSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_PERSON_NAME_DECODER.decode(row["name"]),
            )
            for row in result
        ]
