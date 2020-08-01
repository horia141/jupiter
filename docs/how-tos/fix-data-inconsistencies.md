# Fix Data Inconsistencies

Sometimes you will receive an error that a certain Notion entity does not exist when it should, or that it exists
when it should not. What this means is that the local storage and Notion are not in sync anymore. It can result from a
failed synchronisation command, or some other sort of failure. It's _natural_ for this to happen occasionally, as in
general the sync is not "transactional".

Luckily, it's relatively easy to fix. The synchronisation command `sync` has some special options to address a situation
like this. You can run:

```bash
$ jupiter --verbose sync --anti-entropy --drop-all-notion
```

This command will essentially remove any extra Notion entries, and recreate everything from the local storage. So you
might lose some work if you have not managed to sync it back. Be aware!

You can also filter with the various standard `sync` options: `--project`, `--target`, etc.

You'll have to wait a while while it does its thing. Possibly several hours depending on the size of your workspace.

## Details

The command is essentially a regular synchronisation with some extra bits:

* `--anti-entropy` removes any duplicates it finds, based on the name. Most times this will not cause information loss!
* `--drop-all-notion` removes all Notion entities and then recreates them from the local storage. Sometimes this will
  cause information loss.
