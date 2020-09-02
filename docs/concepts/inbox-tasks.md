# Inbox Tasks

A task is some atomic unit of work. Tasks live in the “inbox”. A task is ideal
to model work which can be done in anything from a minute to a day (excluding
wait or ide times). They can be created by hand, or automatically as recurring
tasks for a certain period.

For example, you can have a task like "Change AC filter", or "Take visa papers to
embassy", or "Research team off-site locations".

Tasks have a _status_, which can be one of:

* _Accepted_: all tasks you created by hand should start with this status. It means
  you’re going to start working on the task in the near future.
* _Recurring_: all tasks you created via recurring tasks and `jupiter gen`
  start with this status. It means you’re going to start working on the task in the
  near future.
* _In Progress_: all tasks you’re currently working on should be placed in this
  status. Once you start working on a task you should move it to this status, and
  keep it there until it’s finished or the parts that depend on you are done, and
  you can move in the “Blocked” state.
* _Blocked_: all tasks that are currently handled by _someone else_, and their
  completion is not in your hands. Once your part of the task is done, you should
  move it to the “Blocked” status. It can move back and forth to “In Progress”,
  and then to “Not Done” or “Done”.
* _Done_: all tasks that are finished, with the desired outcome.
* _Not Done_: all tasks that are finished, but not with the desired outcome.
* _Archived_: tasks which have been archived via `jupiter gc` are moved here. You can also achieve them via manually
  changing their status too.
* _No Status_: tasks which you perhaps created, but don’t plan on actioning in any
  way.

In the Inbox, you can see tasks in a sort of Kanban board, organised by status like
this:

![Inbox image](../assets/concepts-inbox.png)

The state evolution diagram is:

![Task states](../assets/concepts-task-states.png)

You can create a task via regular Notion mechanisms (pressing the various "New" buttons),
or Jupiter can create one for you from the recurring tasks templates via
`jupiter gen`. You can remove a task by simply removing the Notion record of it.

Tasks have a deadline. It’s optional, but it’s strongly recommended you add one
as a goal setting rule.

Tasks can also be labeled according to the [Eisenhower matrix](https://www.eisenhower.me/eisenhower-matrix/),
as either _urgent_ or _important_.

Tasks also have a notion of _difficulty_. They can be catalogued as `Easy`, `Medium` or `Hard`. These inform
the way certain views are sorted. But there's no other semantic meaning attached to these categories though.

In Notion a task might look like this:

![Task image](../assets/concepts-task.png)

The “From Script”, “Recurring Period” and “Recurring Timeline” fields are relevant
only for recurring tasks.

## The Inbox

The inbox is a representation of your current work, as well as the work you recently
finished or will recently start. It's a collection of tasks. They are created here
in the “Accepted” or “Recurring” states, depending on who created them (you, or
the system via `jupiter gen`, respectively).

The inbox looks like a Kanban board usually, with the various states of a task as
columns.

![Inbox image](../assets/concepts-inbox.png)

There are multiple views for the inbox though right now:

* _Kanban All_: views all tasks in the inbox as a Kanban board.
* _Database_: views all tasks in the inbox as a Excel-like table.
* _Kanban Due $InPeriod Or Exceeded_: views all tasks due in a certain period
  (week or month) or those that have exceeded their deadlines as a Kanban board.
* _Not Completed By Date_: views all not done tasks in a calendar. Having due
  dates is important for this purpose.

Here’s a sneak peak at some views:
![Inbox database](../assets/concepts-inbox-database.png)

![Inbox calendar](../assets/concepts-inbox-calendar.png)
.