# Clients

There are multiple ways for interacting with Thrive.

## The Web App

There is a Thrive web app that you can [access online](https://app.get-thriving.com).
It only works in [global hosted mode](hosting-options.md) or self hosted mode, 
and will store all the account's and workspace's data on infrastructure run by the Thrive organisation. This is the preffered
way to use the system, both for ergonomic and ease of access reasons.

## The Desktop App (macOS)

This is an app that you can download an run like a local native app.

It currently works on MacOS in global hosted and self hosted mode.

## The Mobile App (iOS, Android)

Thrive is also available as a mobile app for both iOS and Android devices. The mobile app works in global hosted and self hosted modes, providing access to your workspace on the go. You can download it from the respective app stores.

Only works in the global hosted mode.

## The Progressive Web App (PWA)

Additionally, the web app is also available as a Progressive Web App (PWA). This means you can "install" it directly from your browser to your device's home screen, providing a more native app-like experience. The PWA works on both desktop and mobile devices, offering offline capabilities and quick access to your workspace.

Works in the global hosted and self hosted mode.

## The CLI

There is a Thrive CLI app that you can [dowload](../how-tos/install.md). It only works in
[local mode](hosting-options.md) and will store all the account's and workspace's
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
