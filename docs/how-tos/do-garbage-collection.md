# Do Garbage Collection

Notion is a great tool, but some of the ways in which Jupiter works don't play that _well_ with it. For example, even
light usage will cause hundreds of inbox tasks in a project. As the number of tasks increases, it'll become harder
and harder for Notion to handle them[1] performance wise. Views will load slower, `sync` operations will take longer
and longer to execute, etc.

Furthermore, you're usually interested in the time period around the present time. Tasks you finished one year ago
won't really be relevant.

To address both issues the `gc` command can be used. It's run like so:

```bash
$ jupiter gc
```

You can filter by project, and even tell it to work in parts. But in broad terms, what it'll do is:

* Archive all done inbox tasks and big plans.
* Correct data drift issues - sometimes you'll get duplicate entries for what should be the same task or big plan.
  Garbage collection will make sure only one copy remains. Checkout [this article](./fix-data-inconsistencies.md) for
  details
* Actually remove all archived inbox tasks, big plans, habits, etc from Notion.

It's good to run `gc` periodically. Once a week or so is enough depending on the volume of work you're handling.

---
[1] Mostly because of the way Jupiter sets up Notion, not necessarily because of an intrinsic issue with Notion.