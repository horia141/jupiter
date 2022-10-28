# Garbage Collection

Garbage collection is a periodic action you must perform. It cleans up unneeded structures on Notion side,
making operations faster, and Notion snappier.

Doing garbage collection essentially means running the `gc` command like so:

```bash
$ jupiter gc
```

You can filter by project, and even tell it to work in parts. But in broad terms, what it'll do is:

* Archive all done inbox tasks and big plans.
* Archive all Slack tasks whose corresponding inbox task is completed or archived.
* Archive all email tasks whose corresponding email task is completed or archived.
* Correct data drift issues - sometimes you'll get duplicate entries for what should be the same task or big plan.
  Garbage collection will make sure only one copy remains. Checkout
  [this article](../how-tos/fix-data-inconsistencies.md) for details.
* Actually remove all archived inbox tasks, big plans, habits, chores, smart list items, metric entries,
  persons, slack tasks, email tasks, etc from Notion.

How often you run it depends on how heavily you're using Jupiter. When the number of "done" tasks reaches 1-200, it's
probably the right time. For most people this might mean running it everywhere from monthly to once a week.
