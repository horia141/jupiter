# Clients

There are multiple ways for interacting with Thrive.

## The Web App

There is a Thrive web app that you can [access online](https://app.get-thriving.com).
It only works in [hosted mode](hosted-vs-local-mode.md) and will store all the account's and
workspace's data on infrastructure run by the Thrive organisation. This is the preffered
way to use the system, both for ergonomic and ease of access reasons.

## The CLI App

There is a Thrive CLI app that you can [dowload](../how-tos/install.md). It only works in
[local mode](hosted-vs-local-mode.md) and will store all the account's and workspace's
data on your local machine. Otherwise all functionality is the same.

You can run

```bash
thrive --help
```

To get online help from the app.

A typical command interaction might look like:

```bash
thrive inbox-task-show
thrive inbox-task-update --id 5 --status done
thrive gc
thrive report
```
