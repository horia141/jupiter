# Projects

The workspace contains _one or more_ _projects_. If the workspace is where all the
work happens, a project is where some part of the work happens. Usually some
coherent subset of it.

For example, you can have a project for your personal goal tracking, and one for
your career goal tracking etc. In most cases just one or two projects are enough,
and they should be very long lived things.

Projects are created via the `jupiter project-create --key $projectKey --name "Project Name"`
command. `jupiter project-create` is idempotent. There's no way to create a project from Notion
however. The key is a unique identifier for the project, and must be some nice string with no spaces
or funny characters like `personal` or `work`. It will be used as a reference to the project
in other commands.

After creating a project, you’ll see something like the following in the Notion
left hand bar - here with two Jupiter created pages (“Inbox” and “Big Plan”) and one
regular Notion page (“Blog Ideas”):

![Projects image](../assets/concepts-projects.png)

## Projects Properties

On their own, projects have a single property - their name.

## Projects Interactions Summary

You can:

* Create a project via `projects-create`.
* Remove a project via `projects-archive`.
* Change the name via `projects-set-name`.
* See a summary of the projects via `projects-show`.
