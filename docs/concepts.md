There’s a bunch of _concepts_ Jupiter uses. This page will document them, describe _how_ they’re meant to be used, present the various options they have, etc. It’ll also try to link them with the current version of the system. But they’re not really _tied_ to it. As the system evolves, the concepts should stay the same.

When referencing Jupiter commands, we’ll use `jupiter foo` instead of the current Docker based `docker run -it --rm --name jupiter-app -v $(pwd):/data --env TZ=Europe/Bucharest jupiter foo`. We’ll get there _sometime_ too, but for the sake of brevity it’s easier this way.

Note that most commands are idempotent.

# Workspace

All work inside Jupiter takes place in a _workspace_. When you use `jupiter init` in a local directory you’re starting up your workspace. The local directory, the Notion.so pages created are all part of the workspace. You can have multiple workspaces, and they can even share the same Notion.so space/account, but realistically it makes sense to use just one. All further concepts we discuss are _relative_ to the workspace.

Workspaces are created via the `jupiter init ${user.yaml}` command. The `user.yaml` file has the following format:

```yaml
token_v2: "YOUR_SECRET_HERE"
space_id: "YOUR_SPACE_ID_HERE"

name: "Plans"

vacations:
  - start: 2020-02-10

    end: 2020-02-20
```

`jupiter init` is idempotent, and is a good way to update workspaces as newer versions of the tool appear.

The `name` field is self explanatory, and the `token_v2` and `space_id` ones are covered in the [tutorial section](https://github.com/horia141/jupiter/blob/master/docs/tutorial.md). `vacations` however is an array of entries describing what vacations you have planned. These will be taken into account when scheduling recurring tasks for example.

After creating a workspace, you’ll see something like the following in the Notion left hand bar - here with a couple of projects too at the top-level under “Plans”, namely “Personal”, “Engineer 2.0”, “Work @Bolt”, etc:

![Workspace image](assets/concepts-workspace.png)

# Projects

The workspace contains _one or more_ _projects_. If the workspace is where all the work happens, a project is where some part of the work happens. Usually some coherent part of it. For example, you can have a project for your personal goal tracking, and one for your career goal tracking etc. In most cases just one or two projects are enough, and they should be very long lived things.

Projects are created via the `jupiter create-project ${user.yaml} ${project.yaml}` command. The `project.yaml` file has the following format:

```yaml
name: “Work”
key: work

groups:
  # We’ll go into details here when speaking about recurring tasks.
```

`jupiter create-project` is idempotent, and is a good way to update projects as newer versions of the tool appear.

After creating a project, you’ll see something like the following in the Notion left hand bar - here with two Jupiter created pages (“Inbox” and “Big Plan”) and one regular Notion page (“Blog Ideas”):

![Projects image](assets/concepts-projects.png)


# Tasks

A task is some atomic unit of work. Tasks live in the “inbox”. They can be created by hand, or automatically as recurring tasks for a certain period.

Tasks have a _status_, which can be one of:
* _Accepted_: all tasks you created by hand should start with this status. It means you’re going to start working on the task in the near future.
* _Recurring_: all tasks you created via recurring tasks and `jupiter upsert-tasks` start with this status. It means you’re going to start working on the task in the near future.
* _In Progress_: all tasks you’re currently working on should be placed in this status. Once you start working on a task you should move it to this status, and keep it there until it’s finished or the parts that depend on you are done, and you can move in the “Blocked” state.
* _Blocked_: all tasks that are currently handled by _someone else_, and their completion is not in your hands. Once your part of the task is done, you should move it to the “Blocked” status. It can move back and forth to “In Progress”, and then to “Not Done”, “Done”.
* _Not Done_: all tasks that are finished, but not with the desired outcome.
* _Done_: all tasks that are finished, with the desired outcome.
* _Archived_: tasks which have been archived via `jupiter archive-done-tasks` are moved here. You can also achieve them via manually changing their status too.
* _No Status_: tasks which you perhaps created, but don’t plan on actioning in any way.

In the Inbox, you can see tasks in a sort of Kanban board, organised by status like this:

![Inbox image](assets/concepts-inbox.png)

The state evolution diagram can be:

![Task states](assets/concepts-task-states.png)

Tasks have a deadline. It’s optional, but it’s strongly recommended you add one as a goal setting rule.

Tasks can also be labeled according to the [Eisenhower matrix](https://www.eisenhower.me/eisenhower-matrix/), as either _urgent_ or _important_.

In Notion a task might look like this:

![Task image](assets/concepts-task.png)

The “From Script”, “Recurring Period” and “Recurring Timeline” fields are relevant only for recurring tasks.

# The Inbox

The inbox is a representation of your current, near past and near future work. It’s where the tasks live. They are created here in the “Accepted” or “Recurring” states, depending on who created them (you, or the system via `jupiter upsert-tasks`, respectively).

The inbox looks like a kanban board usually, with the various states of a task as columns.

![Inbox image](assets/concepts-inbox.png)

There are multiple views for the inbox though right now:
* _Kanban All_: views all tasks in the inbox as a Kanban board.
* _Database_: views all tasks in the inbox as a Excel-like table.
* _Kanban Due $InPeriod Or Exceeded_: views all tasks due in a certain period (week or month) or those that have exceeded their deadlines as a Kanban board.
* _Not Completed By Date_: views all not done tasks in a calendar. Having due dates is important for this purpose.
Here’s a sneak peak at them:

![Inbox database](assets/concepts-inbox-database.png)
![Inbox calendar](assets/concepts-inbox-calendar.png)

The inbox can get cluttered with time as you finish more and more tasks. The filtered views help a bit, but due to limitations in how Jupiter interacts with Notion, after some point there are performance issues. Some things you can do to do garbage collection is running:
Task archival via `jupiter archive-done-tasks {user} {project}`. This operation simply changes any tasks with the “Not Done” or “Done” status to the “Archived” status, which essentially makes them invisible.
Task removal via `jupiter remove-archived-tasks {user} {project}`. This operation actually removes the tasks with the “Archived” status from Notion. They’ll be available in the Notion trash, but quite hard to recover. Note - this will be improved in the future.

# Big Plans

# Recurring Tasks

Each project has big plans, recurring tasks, and the inbox.

Finally there are tasks.

Going back to the workspace level there are also vacations.
