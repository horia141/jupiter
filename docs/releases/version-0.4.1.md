# Version 0.4.1

Launched on 2020/09/02

This version introduces:

* Brand new and expanded [docs](https://jupiter-goals.readthedocs.io/).
* Massive rethink of the way storage is handled - new format is simpler and more robust.
* Added the ability to build [reports](../concepts/reporting.md) for past activity.
* Made a unified `sync` [command](../concepts/notion-local-sync.md) instead of the various per-entity ones.
* Add a single `gc` [command](../concepts/garbage-collection.md) for clearing up stuff on Notion-side.
* Added commands to _hard remove_ entities from both [local storage](../concepts/local-storage.md) and Notion.
* Added the _timezone_ as a workspace-level setting.
* Introduced the concepts of _chores_ and _habits_. A recurring task can be one of these, and they'll get slightly
  different treatment when building reports, for example.
* Got rid of the _group_ property for recurring tasks.
* Helpful error links to the "How Tos" section on certain errors.
* A `--version` argument to the [CLI](../concepts/jupiter-cli.md).
* Added type annotations to the whole codebase.
* Removed the `--dry-run` argument to certain commands.
* Added many log messages, and added the ability to control the log levels shown, as well as a general `--verbose` flag.
* Upgrade to Python `3.8.5`.
* Many bugfixes and performance improvements.
