# Do Garbage Collection

As you work in your workspace, you'll make quick work of your tasks. These will gather in your "done" and
"not done" columns and start to lose their relevance.

In order not to clutter your workspace, you can _garbage collect_ them. This will _archive_ the completed tasks
and big plans. You will still be able to access them, but they won't appear in the inbox task view.

It's good to run `gc` periodically. Once a week or so is enough depending on the volume of work you're handling.

## With The Web App

In order to perform garbage collection in the webapp you need to go to the "Garbage Collect" left-hand side menu
item and click "Garbage Collect".

![GC](../assets/gc.png)

## With the CLI App

The same thing can be achieved with the  `gc` command of the CLI, like so:

```bash
$ jupiter gc
```