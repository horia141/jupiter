# Metrics

Metrics are a measure of the evolution in time of some aspect of your life. It is often useful to
quantify certain aspects of your life, and keep special tabs on it. Metrics allow you to track
your weight, your retirement savings, days gone to the gym, miles run, etc.

In the workspace overview, you can view the set of metrics:

![Metrics](../assets/concepts-metrics-overview.png)

Each metric contains many entries or records, for example:

![Metric entries](../assets/concepts-metrics-entries.png)

Much like [projects](projects.md), metrics are created via the
`jupiter metrics-create --metric $smartListKey --name "Metric Name"` command. The command is
idempotent. The key plays the same part it does for a project, is a unique identifier for the
metric, and must be some nice string with no spaces or funny characters like `books` or `movies`.
It will be used as a reference to the project in other commands.

Metrics have a name. It's the nicely looking counterpart to the key.

Metrics can also have a _unit_. It adds extra info about what exactly you're recording - weight,
currency, the count of an event, etc.

Metrics can also have a collection period. This isn't yet used.

## Interaction Summary

You can:

* Create a metric via `metrics-create`.
* Remove a metric via `metrics-archive`.
* Change the name via `metrics-set-name`, or by changing the name of the page in Notion.
* Change the collection period via `metrics-set-collection-period`. This cannot be changed from Notion.
* Change the unit via `metrics-set-unit`. This cannot be changed from Notion.
* See a summary of the metrics via `metrics-show`.

## Entries

Metric entries are the records of the value of a certain metric at a certain time.

Metric entries have a _collection time_ - the time they were recorded.

They also have a _value_ - the actual value for the metric at that particular time.

Metric entries can also have some notes attached to them, for any extra info you might want to add.

In general, you're going to create entries from Notion, and use [sync](notion-local-sync.md) to bring them
over to the [local store](local-storage.md).

## Entries Interaction Summary

You can:

* Create a metric entry via `metrics-entry-create`, or by creating a new entry in the appropriate Notion table.
* Remove a metric entry via `metrics-entry-archive`, or by clicking the archive checkbox in Notion.
* Change the collection time of a metric entry via `metrics-entry-set-collection-time`, or by changing the collection
  time from the Notion row.
* Change the value of a metric entry via `metrics-entry-set-value`, or by changing the value from the Notion row.
* Change the notes of a metric entry via `metrics-entry-set-notes`, or by changing the notes from the Notion row.
* Show info about the metric entrys via `metrics-entry-show`.
