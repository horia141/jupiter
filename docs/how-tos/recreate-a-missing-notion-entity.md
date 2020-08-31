# Recreate A Missing Notion Entity

Most operations you run from the [CLI](../concepts/jupiter-cli.md) involve doing some operation on the
[local store](../concepts/local-storage.md), then mirroring the operation on Notion side. This does not happen
_atomically_ and there's a chance the first stage succeeds while the second one fails. This might occur because
the network is down or Notion has some issues, or some bug in Jupiter itself.

In any case, fixing such issues is simple. Simply [sync](../concepts/notion-local-sync.md) like so:

```bash
$ jupiter sync
```

This will catch the missing Notion entity and create it there.
