# Sync From Notion To Local

Regular [sync](../concepts/notion-local-sync.md) gives precedence to the Notion version of an entity - vacation, inbox
task, project, etc. Most of the times this is what you want, since you're using it as the main interaction surface.
But sometimes you want to use [local storage](../concepts/local-storage.md) as the source of truth.

Luckily, `sync` can be run in this way too via:

```bash
$ jupiter sync --prefer local
```

This won't mean new Notion-side entities won't be created, just that for already existing ones, the local versions will
be used. Be careful that you'll lose your Notion-side changes this way. All the other filtering options work, so you
can be really surgical about this sync.
