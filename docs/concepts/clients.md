# Clients

There are multiple ways for interacting with Jupiter.

## The Web App

There is a Jupiter web app that you can [access online](https://jupiter-webui.onrender.com).
It only works in [hosted mode](hosted-vs-local-mode) and will store all the account's and
workspace's data on infrastructure run by the Jupiter organisation. This is the preffered
way to use the system, both for ergonomic and ease of access reasons.

## The CLI App

There is a Jupiter CLI app that you can [dowload](../how-tos/install.md). It only works in
[local mode](hosted-vs-local-mode.md) and will store all the account's and workspace's
data on your local machine. Otherwise all functionality is the same.

You can run

```bash
jupiter --help
```

To get online help from the app.

A typical command interaction might look like:

```bash
jupiter inbox-task-show
jupiter inbox-task-update --id 5 --status done
jupiter gc
jupiter report
```
