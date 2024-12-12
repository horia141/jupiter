# Version 0.3.0

Launched on 2020/04/08

This version introduces:

* Major overhaul of interaction with projects and recurring tasks. Basically, there's no more working directly
  with YAML files. Instead, there are CLI commands and Notion boards dedicated for this, much like there are
  for vacations. Checkout [concepts](../concepts/overview.md) for an up-to-date view of all that's possible now.
* The `recurring-tasks-*` and `project-*` command sets were added for managing this whole thing.
* Recurring tasks can now be suspended. While suspended, no new instances will be generated for them. This allows
  folks to gracefully handle situations when a habit or chore can't be done, due to external factors, for example.
  This feature is obviously inspired by the Coronavirus situation.
