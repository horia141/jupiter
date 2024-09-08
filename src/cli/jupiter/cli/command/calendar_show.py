"""Command for loading a calendar."""
from typing import cast

from jupiter.cli.command.command import LoggedInReadonlyCommand
from jupiter.cli.command.rendering import (
    date_with_label_to_rich_text,
    entity_name_to_rich_text,
    period_to_rich_text,
    person_birthday_to_rich_text,
    time_in_day_to_rich_text,
)
from jupiter.core.domain.concept.persons.person_birthday import PersonBirthday
from jupiter.core.use_cases.application.calendar.load_for_date_and_period import (
    CalendarEventsEntries,
    CalendarEventsStats,
    CalendarLoadForDateAndPeriodResult,
    CalendarLoadForDateAndPeriodUseCase,
)
from jupiter.core.use_cases.infra.use_cases import AppLoggedInReadonlyUseCaseContext
from rich.console import Console
from rich.text import Text
from rich.tree import Tree


class CalendarShow(
    LoggedInReadonlyCommand[
        CalendarLoadForDateAndPeriodUseCase, CalendarLoadForDateAndPeriodResult
    ]
):
    """Command for loading a calendar."""

    def _render_result(
        self,
        console: Console,
        context: AppLoggedInReadonlyUseCaseContext,
        result: CalendarLoadForDateAndPeriodResult,
    ) -> None:
        header_text = Text("📅 ")
        header_text.append(period_to_rich_text(result.period))
        header_text.append(" calendar for")
        header_text.append(date_with_label_to_rich_text(result.right_now, ""))

        rich_tree = Tree(header_text)

        if result.entries:
            # Process the full days events

            full_day_events_tree = Tree(
                "Full Days Events", guide_style="bold bright_blue"
            )

            self._build_birthdays(result.entries, full_day_events_tree)

            self._build_schedule_full_days(result.entries, full_day_events_tree)

            rich_tree.add(full_day_events_tree)

            # Process the in day events

            in_day_events_tree = Tree("In Day Events", guide_style="bold bright_blue")

            self._build_inbox_tasks(result.entries, in_day_events_tree)

            self._build_schedule_in_day(result.entries, in_day_events_tree)

            rich_tree.add(in_day_events_tree)

        if result.stats:
            # Process the stats

            stats_tree = self._build_stats(result.stats)

            rich_tree.add(stats_tree)

        console.print(rich_tree)

    def _build_birthdays(
        self, entries: CalendarEventsEntries, full_day_events_tree: Tree
    ) -> None:
        for person_entry in sorted(
            entries.person_entries,
            key=lambda pe: (
                pe.birthday_time_event.start_date,
                pe.birthday_time_event.end_date,
            ),
        ):
            person = person_entry.person

            person_text = Text("Birthday for ")
            person_text.append(entity_name_to_rich_text(person.name))
            person_text.append(" ")
            person_text.append(
                person_birthday_to_rich_text(cast(PersonBirthday, person.birthday))
            )

            full_day_events_tree.add(person_text)

    def _build_schedule_full_days(
        self, entries: CalendarEventsEntries, full_day_events_tree: Tree
    ) -> None:
        for schedule_event_full_days_entry in sorted(
            entries.schedule_event_full_days_entries,
            key=lambda se: (se.time_event.start_date, se.time_event.end_date),
        ):
            schedule_event_full_days = schedule_event_full_days_entry.event
            time_event = schedule_event_full_days_entry.time_event
            shcedule_stream = schedule_event_full_days_entry.stream

            schedule_event_full_days_text = Text("")
            schedule_event_full_days_text.append(
                entity_name_to_rich_text(schedule_event_full_days.name)
            )
            schedule_event_full_days_text.append(" ")
            schedule_event_full_days_text.append(
                date_with_label_to_rich_text(time_event.start_date, "from")
            )
            schedule_event_full_days_text.append(" ")
            schedule_event_full_days_text.append(
                date_with_label_to_rich_text(time_event.end_date, "to")
            )
            schedule_event_full_days_text.append(" for stream ")
            schedule_event_full_days_text.append(
                entity_name_to_rich_text(shcedule_stream.name)
            )

            full_day_events_tree.add(schedule_event_full_days_text)

    def _build_inbox_tasks(
        self, entries: CalendarEventsEntries, in_day_events_tree: Tree
    ) -> None:
        for inbox_task_entry in sorted(
            entries.inbox_task_entries,
            key=lambda it: (
                it.time_events[0].start_date,
                it.time_events[0].start_time_in_day,
                it.time_events[0].duration_mins,
            ),
        ):
            inbox_task = inbox_task_entry.inbox_task
            time_event = inbox_task_entry.time_events

            inbox_task_text = Text("")
            inbox_task_text.append(entity_name_to_rich_text(inbox_task.name))
            inbox_task_text.append(" ")
            inbox_task_text.append(
                date_with_label_to_rich_text(time_event[0].start_date, "from")
            )
            inbox_task_text.append(" at ")
            inbox_task_text.append(
                time_in_day_to_rich_text(time_event[0].start_time_in_day)
            )
            inbox_task_text.append(
                f" that lasts for {time_event[0].duration_mins} minutes"
            )

            in_day_events_tree.add(inbox_task_text)

    def _build_schedule_in_day(
        self, entries: CalendarEventsEntries, in_day_events_tree: Tree
    ) -> None:
        for schedule_event_in_day_entry in sorted(
            entries.schedule_event_in_day_entries,
            key=lambda se: (
                se.time_event.start_date,
                se.time_event.start_time_in_day,
                se.time_event.duration_mins,
            ),
        ):
            schedule_event_in_day = schedule_event_in_day_entry.event
            time_event = schedule_event_in_day_entry.time_event
            schedule_stream = schedule_event_in_day_entry.stream

            schedule_event_in_day_text = Text("")
            schedule_event_in_day_text.append(
                entity_name_to_rich_text(schedule_event_in_day.name)
            )
            schedule_event_in_day_text.append(" ")
            schedule_event_in_day_text.append(
                date_with_label_to_rich_text(time_event.start_date, "from")
            )
            schedule_event_in_day_text.append(" at ")
            schedule_event_in_day_text.append(
                time_in_day_to_rich_text(time_event.start_time_in_day)
            )
            schedule_event_in_day_text.append(
                f" that lasts for {time_event.duration_mins} minutes"
            )

            schedule_event_in_day_text.append(" for stream ")
            schedule_event_in_day_text.append(
                entity_name_to_rich_text(schedule_stream.name)
            )

            in_day_events_tree.add(schedule_event_in_day_text)

    def _build_stats(self, stats: CalendarEventsStats) -> Tree:
        stats_tree = Tree("Stats", guide_style="bold bright_blue")

        for stat in stats.per_subperiod:
            per_subperiod_text = Text("")
            per_subperiod_text.append(
                date_with_label_to_rich_text(stat.period_start_date, "From")
            )

            per_subperiod_tree = Tree(per_subperiod_text)

            per_subperiod_tree.add(
                Text(
                    f"{stat.schedule_event_full_days_cnt} scheduled full day events",
                    style="gray62"
                    if stat.schedule_event_full_days_cnt == 0
                    else "default",
                )
            )
            per_subperiod_tree.add(
                Text(
                    f"{stat.schedule_event_in_day_cnt} scheduled in day events",
                    style="gray62"
                    if stat.schedule_event_in_day_cnt == 0
                    else "default",
                )
            )
            per_subperiod_tree.add(
                Text(
                    f"{stat.inbox_task_cnt} inbox tasks",
                    style="gray62" if stat.inbox_task_cnt == 0 else "default",
                )
            )
            per_subperiod_tree.add(
                Text(
                    f"{stat.person_birthday_cnt} birthday events",
                    style="gray62" if stat.person_birthday_cnt == 0 else "default",
                )
            )

            stats_tree.add(per_subperiod_tree)

        return stats_tree
