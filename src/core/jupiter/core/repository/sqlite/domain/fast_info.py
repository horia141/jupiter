"""The SQLite implementation of the fast info repository."""

import json

from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.calendar.calendar_stream_name import CalendarStreamName
from jupiter.core.domain.chores.chore_name import ChoreName
from jupiter.core.domain.core.entity_icon import EntityIconDatabaseDecoder
from jupiter.core.domain.fast_info_repository import (
    BigPlanSummary,
    CalendarStreamSummary,
    ChoreSummary,
    FastInfoRepository,
    HabitSummary,
    InboxTaskSummary,
    MetricSummary,
    PersonSummary,
    ProjectSummary,
    SmartListSummary,
    VacationSummary,
)
from jupiter.core.domain.habits.habit_name import HabitName
from jupiter.core.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.core.domain.metrics.metric_name import MetricName
from jupiter.core.domain.persons.person_name import PersonName
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.domain.smart_lists.smart_list_name import SmartListName
from jupiter.core.domain.vacations.vacation_name import VacationName
from jupiter.core.framework.base.entity_id import EntityId, EntityIdDatabaseDecoder
from jupiter.core.framework.base.entity_name import EntityNameDatabaseDecoder
from jupiter.core.repository.sqlite.infra.repository import SqliteRepository
from sqlalchemy import text

_ENTITY_ID_DECODER = EntityIdDatabaseDecoder()
_CALENDAR_STREAM_NAME_DECODER = EntityNameDatabaseDecoder(CalendarStreamName)
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
            await self._connection.execute(
                text(query), {"parent_ref_id": parent_ref_id.as_int()}
            )
        ).fetchall()
        return [
            VacationSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_VACATION_NAME_DECODER.decode(row["name"]),
            )
            for row in result
        ]

    async def find_all_calendar_stream_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> list[CalendarStreamSummary]:
        """Find all summaries about calendar streams."""
        query = """select ref_id, name from calendar_stream where calendar_stream_domain_ref_id = :parent_ref_id"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            await self._connection.execute(
                text(query), {"parent_ref_id": parent_ref_id.as_int()}
            )
        ).fetchall()
        return [
            CalendarStreamSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_CALENDAR_STREAM_NAME_DECODER.decode(row["name"]),
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
            await self._connection.execute(
                text(query), {"parent_ref_id": parent_ref_id.as_int()}
            )
        ).fetchall()
        return [
            ProjectSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                parent_project_ref_id=_ENTITY_ID_DECODER.decode(
                    str(row["parent_project_ref_id"])
                )
                if row["parent_project_ref_id"]
                else None,
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
            await self._connection.execute(
                text(query), {"parent_ref_id": parent_ref_id.as_int()}
            )
        ).fetchall()
        return [
            InboxTaskSummary(
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
        query = """select ref_id, name from habit where habit_collection_ref_id = :parent_ref_id"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            await self._connection.execute(
                text(query), {"parent_ref_id": parent_ref_id.as_int()}
            )
        ).fetchall()
        return [
            HabitSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_HABIT_NAME_DECODER.decode(row["name"]),
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
            await self._connection.execute(
                text(query), {"parent_ref_id": parent_ref_id.as_int()}
            )
        ).fetchall()
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
            await self._connection.execute(
                text(query), {"parent_ref_id": parent_ref_id.as_int()}
            )
        ).fetchall()
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
            await self._connection.execute(
                text(query), {"parent_ref_id": parent_ref_id.as_int()}
            )
        ).fetchall()
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
        query = """select ref_id, name, icon from metric where metric_collection_ref_id = :parent_ref_id"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            await self._connection.execute(
                text(query), {"parent_ref_id": parent_ref_id.as_int()}
            )
        ).fetchall()
        return [
            MetricSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_METRIC_NAME_DECODER.decode(row["name"]),
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
            await self._connection.execute(
                text(query), {"parent_ref_id": parent_ref_id.as_int()}
            )
        ).fetchall()
        return [
            PersonSummary(
                ref_id=_ENTITY_ID_DECODER.decode(str(row["ref_id"])),
                name=_PERSON_NAME_DECODER.decode(row["name"]),
            )
            for row in result
        ]
