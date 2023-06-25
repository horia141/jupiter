"""The SQLite implementation of the fast info repository."""
from typing import Final, List

from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.chores.chore_name import ChoreName
from jupiter.core.domain.entity_icon import EntityIcon
from jupiter.core.domain.fast_info_repository import (
    BigPlanSummary,
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
from jupiter.core.framework.base.entity_id import EntityId
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteFastInfoRepository(FastInfoRepository):
    """The Sqlite based implementation for the fast info repository."""

    _connection: Final[AsyncConnection]

    def __init__(self, connection: AsyncConnection) -> None:
        """Constructor."""
        self._connection = connection

    async def find_all_vacation_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[VacationSummary]:
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
                ref_id=EntityId.from_raw(str(row["ref_id"])),
                name=VacationName.from_raw(row["name"]),
            )
            for row in result
        ]

    async def find_all_project_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[ProjectSummary]:
        """Find all summaries about projects."""
        query = """select ref_id, name from project where project_collection_ref_id = :parent_ref_id"""
        if not allow_archived:
            query += " and archived=0"
        result = (
            await self._connection.execute(
                text(query), {"parent_ref_id": parent_ref_id.as_int()}
            )
        ).fetchall()
        return [
            ProjectSummary(
                ref_id=EntityId.from_raw(str(row["ref_id"])),
                name=ProjectName.from_raw(row["name"]),
            )
            for row in result
        ]

    async def find_all_inbox_task_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[InboxTaskSummary]:
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
                ref_id=EntityId.from_raw(str(row["ref_id"])),
                name=InboxTaskName.from_raw(row["name"]),
            )
            for row in result
        ]

    async def find_all_habit_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[HabitSummary]:
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
                ref_id=EntityId.from_raw(str(row["ref_id"])),
                name=HabitName.from_raw(row["name"]),
            )
            for row in result
        ]

    async def find_all_chore_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[ChoreSummary]:
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
                ref_id=EntityId.from_raw(str(row["ref_id"])),
                name=ChoreName.from_raw(row["name"]),
            )
            for row in result
        ]

    async def find_all_big_plan_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[BigPlanSummary]:
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
                ref_id=EntityId.from_raw(str(row["ref_id"])),
                name=BigPlanName.from_raw(row["name"]),
                project_ref_id=EntityId.from_raw(str(row["project_ref_id"])),
            )
            for row in result
        ]

    async def find_all_smart_list_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[SmartListSummary]:
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
                ref_id=EntityId.from_raw(str(row["ref_id"])),
                name=SmartListName.from_raw(row["name"]),
                icon=EntityIcon.from_raw(row["icon"]) if row["icon"] else None,
            )
            for row in result
        ]

    async def find_all_metric_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[MetricSummary]:
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
                ref_id=EntityId.from_raw(str(row["ref_id"])),
                name=MetricName.from_raw(row["name"]),
                icon=EntityIcon.from_raw(row["icon"]) if row["icon"] else None,
            )
            for row in result
        ]

    async def find_all_person_summaries(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
    ) -> List[PersonSummary]:
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
                ref_id=EntityId.from_raw(str(row["ref_id"])),
                name=PersonName.from_raw(row["name"]),
            )
            for row in result
        ]
