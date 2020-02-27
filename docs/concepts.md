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

    end: 2020-02-20```

`jupiter init` is idempotent, and is a good way to update workspaces as newer versions of the tool appear.

The `name` field is self explanatory, and the `token_v2` and `space_id` ones are covered in the [tutorial section](https://github.com/horia141/jupiter/blob/master/docs/tutorial.md). `vacations` however is an array of entries describing what vacations you have planned. These will be taken into account when scheduling recurring tasks for example.

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

Each project has big plans, recurring tasks, and the inbox.

Finally there are tasks.

Going back to the workspace level there are also vacations.
