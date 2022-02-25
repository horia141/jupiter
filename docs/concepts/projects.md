# Projects

A project is a larger and longer-term container for work. Think of it as a _label_
for tasks, habits, chores, or big plans.

For example, you can have a project for your personal goal tracking, and one for
your career goal tracking etc. In most cases just one or two projects are enough,
and they should be very long lived things.

Projects are created via the `jupiter project-create --key $projectKey --name "Project Name"`
command. `jupiter project-create` is idempotent. The key is a unique identifier for the project,
and must be some nice string with no spaces or funny characters like `personal` or `work`. It will be
used as a reference to the project in other commands.

After creating a project, you’ll see something like the following in the Notion
left hand bar - here with two Jupiter created pages (“Inbox” and “Big Plan”) and one
regular Notion page (“Blog Ideas”):

![Projects image](../assets/concepts-projects.png)

## Projects Properties

On their own, projects have a single property - their name.

## Projects Interactions Summary

You can:

* Create a project via `projects-create`.
* Change the name via `projects-update`.
* See a summary of the projects via `projects-show`.
