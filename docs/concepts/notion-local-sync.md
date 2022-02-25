# Sync Notion And Local

Syncing is a periodic action you must perform. It makes sure that all of the changes you've done through Notion
are reflected in the [local storage](local-storage.md).

Usually you'd be doing most of your interaction with Jupiter through Notion - it provides a fancy interface for
task creation, big plan management, notes writing, etc. But all the changes you do there aren't automatically
copied over to the local storage, hence operations such as [task generation](tasks-generation.md),
[garbage collection](garbage-collection.md), or [reporting](reporting.md) won't take them into account.

To achieve all the above, you use the `sync` command. It's enough to run it as:

```bash
$ jupiter sync
```

And it will work its magic, creating new entities in Notion locally, updating modified ones, creating entities on
Notion side which are somehow present only locally (perhaps because of some sync error). But it does a bit more. It
also updates Notion-side page structures, recreates links between inbox tasks and their big plans or recurring tasks,
updates schemas, etc.

Syncing can be very targeted, run `juputer sync --help` to see the full list of options. But you can:

* Sync just the pages structure, or the workspace, or projects, or just one of the classes of entities. Or any
  combination.
* Sync a particular project, or even a particular entity - like a single inbox task.
* Sync with a preference for the local data. When something like an inbox task is found both on Notion side and on
  the local side, you can select to prefer the data from the local side. A nice restore method.
* By default syncing looks at modified entities to keep it fast, but you can force it to ignore this and do a full
  sync. Be prepare to wait a bit!
* Drop everything on Notion side and restart from the local data! You'll lose unsynced Notion data!

Notice that `sync` is the only command which takes data from Notion and applies it locally. Every other command
first works locally, and then applies the change to Notion. This means you don't need a `sync` to mirror local commands
or to somehow pull in changes done through the CLI.
