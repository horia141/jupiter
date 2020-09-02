# Recurring Tasks

A recurring task is some periodic and atomic unit of work. Recurring tasks live in the
"recurring tasks" view, but they're instantiated as regular tasks in the "inbox". A recurring
task is ideal to model work which needs to be done periodically, like a chore or a habit.

For example, you can have a recurring task like "Clean out AC filters every week", or
"Pay home insurance every month", or "Walk more than 10000 steps every day".

In the recurring tasks view, the task templates might look like this:

![Recurring tasks templates](../assets/concepts-inbox-recurring.png)

## Recurring Tasks Properties

Recurring tasks have a _period_ and a _period interval_. The former is set via the `period`
property and the latter is derived uniquely from this. The period can be one of:

* _Daily_: a task which needs to happen once a day. In a year there will be 365 or 366
  instances of such a task, and the period interval for each one will be each day. The
  intervals are numbered from 1 to 365.
* _Weekly_: a task which needs to happen once a week. In a year there will be 52
  instances of such a task, and the period interval for each one will be the corresponding
  week. The intervals are numbered from 1 to 52.
* _Monthly_: a task which needs to happen once a month. In a year there will be 12
  instances of such a task, and the period interval for each one will be the corresponding
  month. The intervals are numbered from 1 to 12.
* _Quarterly_: a task which needs to happen once a quarter (group of three months). In a
  year there will be 4 instances of such a task, and the period interval for each one will
  be a group of three consecutive months (Jan/Feb/Mar, Apr/May/Jun, Jul/Aug/Sep, and Oct/Nov/Dec).
  The intervals are numbered from 1 to 4.
* _Yearly_: a task which needs to happen once a year. In a year there will be 1 instance
  of such a task, and the period interval for it will be the full year. The intervals
  are numbered by the year.

Notice that the smallest period is the `daily` one, with a period interval of one day. In
general, for a given period interval there can be only one instantiation of a task of that
period.

While in the inbox, the instantiated tasks might look like this - notice the "Weekly" and
"Monthly" labels:

![Inbox with recurring tasks](../assets/concepts-inbox-recurring.png)

The instantiated task in the inbox is constructed from the recurring task template, but
it also changes in the following way:

* The name contains the period interval for which the task is active. So "Pay home
  insurance" becomes "Pay home insurance Mar". The formats are "Mar13" for daily periods,
  "W13" for weekly periods, "Mar" for monthly periods, "Q1" for quarterly periods,
  and "2020" for yearly periods.
* The "From Script", "Recurring Period" and "Recurring Timeline" fields are populated. But
  they are rather implementation details.

Recurring tasks also have a deadline. By default the deadline is the end day of the period
interval, at midnight. You can override it however to specify, via the `due_at_day` and
`due_at_time` properties. They work like so:

* For tasks with daily period, only the `due_at_time` property can be set. For example
  `due_at_time: "17:00"` will mark a task as due at 5PM in the local timezone, as opposed
  to 11:59PM in the local timezone.
* For tasks with weekly and monthly periods, the `due_at_day` and `due_at_time` property
  can be set. For example `due_at_day: 10` will set the deadline of a monthly task
  to be the midnight of the 10th day of the month. Adding `due_at_time: "13:00"` will
  mark it as due at 1PM in the local timezone on the 10th day of the month.
* For tasks with quarterly and yearly periods, the `due_at_month`, `due_at_day` and
  `due_at_time` property can be set. For example `due_at_month: 3` will set the deadline
  of a yearly task to be the midnight of the last day of March. Adding `due_at_day: 10`
  will mark it as due at midnight of the 10th of March. and adding `due_at_time: "13:00"`
  will mark it as due at 1PM on the 10th of March.

In Notion an instantiated task might look like this then:

![Instantiated recurring task image](../assets/concepts-instantiated-recurring-task.png)

Recurring tasks can be configured to skip certain periods via a skip rule. This is
specified via the `skip_rule` property, which can be one of:

* `odd`: skips the odd numbered intervals for the period. More precisely, the day/week/
  month/quarter number within the year is checked to be odd. For yearly periods, the year
  itself should be odd.
* `even`: skips the even numbered intervals for the period. Same rules apply as above.
* A set of values: skips the intervals within this set. For example, if the property is
  `skip_rule: [1, 4, 7]` and `period: "weekly"`then the 1st, 4th and 7th weeks of the year
  are skipped.

A recurring task can be mark as "must do", via the `Must Do` property. Being marked
as such that will cause it to ignore vacations. For example, paying rent or taking some medicine
can't be interrupted by a vacation.

A recurring task can be suspended, via the `Suspended` property. Being marked as such means
that the task won't be generated at all. For example, going to the gym might be suspended while
you're recovering from an illness.

A recurring task can also have a difficulty, just like a regular task. This will be copied
to all the instantiated tasks that are created.

Similarly, a recurring task can have the Eisenhower properties. These will be copied to
all the instantiated tasks that are created.

Recurring tasks are created via the `jupiter gen` command. This has some special
forms too:

* `jupiter gen` is the standard form and inserts all of the
  tasks whose period interval includes today. Thus, all daily tasks will be inserted, and
  all weekly tasks for this week, etc. Of course, if the tasks for this week have already
  been instantiated, they won't be again.
* `jupiter gen --date=YYYY-MM-DD` does an insert as if the day
  were the one given by the `date` argument. Useful for creating tasks in the days before
  the start of a certain week or month.
* `jupiter gen {projectKey} --period=PERIOD` does an insert only on the
  tasks with a certain period. Useful to speed up inserts when you know you only want
  new tasks for the next day or week.

Recurring tasks interact with vacations too. More precisely, if a task's period interval
is fully contained within a vacation, that task won't be instantiated in the inbox via
`jupiter gen`. For example, if you have a vacation from Monday `2020-02-09` to
Sunday `2020-02-15`, then all daily and weekly tasks for that week won't be created, but
all monthly, quarterly and yearly ones will.

The `jupiter gen` command is idempotent, as described above. Furthermore it does
not affect task status, or any extra edits on a particular instance of a task. If any property
of the recurring task template which get copied over to the instance is modified, then the command
will take care to update the instance too. Only archived and removed tasks are regenerated.

## Recurring Tasks Interactions Summary

You can:

* Create a recurring task via `recurring-tasks-create`, or by creating a new entry in the "Recurring Tasks" view.
* Remove a recurring task via `recurring-tasks-remove`, or by removing the entry in the "Recurring Tasks" view.
* Change the name of a recurring task via `recurring-tasks-set-name`, or by changing the name of the task in Notion.
* Change the deadline of a recurring task via `recurring-tasks-set-deadline`, or by changing the deadline of the task
  in Notion.
* Change the difficulty of a recurring task via `recurring-tasks-set-difficulty`, or by changing the difficulty of
  the task in Notion.
* Change the Eisenhower status of a recurring task via `recurring-tasks-set-eisen`, or by changing the status in Notion.
* Change the must do status of a recurring task via `recurring-tasks-set-must-do`, or by changing it in Notion.
* Change the period of a recurring task via `recurring-tasks-set-period`, or by changing it in Notion, by dragging the
  task to another column.
* Change the skip rule of a recurring task via `recurring-tasks-set-skip-rule`, or by changing it in Notion.
* Suspend a recurring task via `recurring-tasks-suspend`, or by checking the attribute in Notion.
* Unsuspend a recurring task via `recurring-tasks-unsuspend`, or by checking the attribute in Notion.
* Show info about the recurring task via `recurring-tasks-show`.
