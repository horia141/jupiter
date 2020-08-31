# Fix Data Inconsistencies

Sometimes you will receive an error that a certain Notion entity does not exist when it should, or that it exists
when it should not. What this means is that the local storage and Notion are not in sync anymore. It can result from a
failed synchronisation command, or some other sort of failure. It's _natural_ for this to happen occasionally, as in
general the sync is not "transactional". Jupiter will try to fix it locally and make it work. But some cases are too
complex for a local fix and require some human intervention.

Luckily, it's relatively easy to fix. [Garbage collection](do-garbage-collection.md) should be enough
most times. You can run it as:

```bash
$ jupiter gc
```

If that isn't enough the `sync` command as a nuclear option, which you can use like so:

```bash
$ jupiter sync --drop-all-notion
```

This command will essentially remove any extra Notion entries, and recreate everything from the local storage. So you
might lose some work if you have not managed to sync it back. Be aware!

You can also filter with the various standard `sync` options: `--project`, `--target`, etc.

You'll have to wait a while while it does its thing. Possibly several hours depending on the size of your workspace.
