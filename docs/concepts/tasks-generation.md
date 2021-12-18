# Tasks Generation

Tasks generation is a periodic action you must perform. It takes the _templates_ that are
[recurring tasks](recurring-tasks.md) and turns them into real [inbox tasks](inbox-tasks.md).
It also generates [metric collection tasks](metrics.md) and [person catch up taks](prm.md)
in a similar fashion.

It needs to be performed daily usually, or the lowest period any of your recurring tasks have.

The command itself is simply called `gen` and you can invoke it as:

```bash
$ jupiter gen
```

By default this will generate tasks with the `daily` period for today. But you can force other periods like so:

```bash
$ jupiter gen --period daily --period weekly --period monthly
```

It's the case that you'll want to run these other versions at the start of a week, month, quarter, or year.

Some things to note:

* The command is idempotent, so you can run it however many times you want and it'll do the right thing.
* Via the `--date` argument you can run generation for a date different than today - either in the future or in the
  past.
* You can limit it for a particular project too via the `--project` option.
* You can filter for specific recurring tasks, metrics, and persons.
* You can choose to generate only particular entities.
* Check the help for more options via `jupiter gen --help`.
