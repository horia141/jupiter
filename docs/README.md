# Documentation

This document is a guide to developing in Jupiter. By reading it you should gain an
understanding of how to develop in this project, and should have a working dev environment
that allows you to do said development.

## Naming

Across this project we'll use Jupiter as the codename for the project. Anything technical
or non-user facing will use this name. Conversely, Thrive should just appear in the
application copy, images, legal material, etc.

## Prepare For Development

Checkout `scripts/setup-for-dev.sh`. It outlines the tools you need to have in order to
develop Jupiter. It's a pretty standard Node & Python development setup. A modern IDE is
implied, though no particular brand is assumed.

After a `git clone jupiter ~/Work/jupiter` kind of setup, you should also run the following:

```bash
% ./scripts/setup-for-dev.sh
```

This will set things up locally inside the local repository for the dev tools we use.
This is Python and Node right now. A venv is created, and a bunch of linters and checkers
are installed. Also all the dependencies from pypi and npm. Where possible, everything
is installed for the local repository, but there are some installed globally via brew.

## A Development Session

When you want to develop a new feature or bugfix you need to activate the new dev
session from a shell first. Then there's some small ceremony about creating a feature branch for the work (see below).

```bash
% source ./scripts/work/new-dev-session.sh
# Set everything up in the Python and Node settings
% ./scripts/work/new-feature work-on-something
# Creates branch feature/work-on-something and switch to it
```

Finally there's commands for running a local instance of Jupiter.

```bash
% ./scripts/run-dev.sh a-test
```

This will start the instance with the name `a-test`. If ommited, the standard name `dev`
is used. You can start as many as you want, and they live independently (use different
DBs, different ports, etc.). You can watch the overview of the started processes and their
logs for easier debugging. Though `npx pm2 logs` is also useful here.

For quick checks you can run `./scripts/fast-lint.sh`. And for the whole test-suite with
linters, type checkers, unit tests, integration tests, etc. you can run `make check` (it'll take a couple minutes).

When you're finished you can run:

```bash
./scripts/close-feature.sh
```

This will perform all ceremonies, merge the branch correctly into `main` and push to GitHub.

> A note on using `./scripts/work/new-feature.sh`, `./scripts/work/new-bugfix.sh`, and other
counterparts: we want to keep hygene of the `main` branch to have a linear history of
features and bugfixes, ocassionally tagged with releases. To enforce these, there's no
straight coding on the `main` branch, and the helper scripts help you setup things
in the right way.

## Environments

The Jupiter infrastructure has a rather crips notion of environments. They operate
on two levels: system and feature.

System environments are the names we give for the code in various distances relative
to users and developers. Code can look at the `Env` enum to understand what environment
they are in.

* There is the `production` environment of which there is only one, and which consists
  of the totality of machines, cloud resources, SaaS services, etc. which handle
  the user data, the user interactions, etc. Crucially this also includes the distributed
  clients that are the `cli` app, the `MacOS` app, the `iOS` and `Android` apps, and
  the code running in all the browsers where the app is running like that. So it's both
  machines we own, and ones our customers own! The code running here corresponds
  to the code at `main:latest` or `main:vX.Y` depending on the distribution model.
  This is considered a `live` environment because it is accessible for users.
* There is the `staging` environmenet of which there can be many, and which are used
  by developers to showcase their work. Every time you create a PR, you also create
  a `staging` environment that runs the code in your particular branch. You can build
  and distribute client apps based on this version too. This is also considered a
  `live` environment because it is accessible to users.
* There is the `dev` enviroment of which there can be many, and which are the ones
  developers create when they're running their work on their dev machines. Every
  time you run `./scripts/run-dev.sh` you're creating/using such an environment.
  This is not considered `local` environment because it is not accessible to users.

Feature environments are a subset of `dev` and `staging` environments. When you specificy a
particular name in `./scripts/run-dev.sh <your-name>` you create such an env for example,
or reuse if you created it before. When you open a PR, the same happens but in a `live`
setting. These environments are separate between each other, and start in a blank but valid state.

## Running Tests

The full test suite is run via `make check`. This runs linters, type checkers, and
various test batteriess on all the sources, config files, etc.

There is `./scripts/fast-lint.sh` that runs just the linters and type checkers and
is used for quicker feedback on the changes that you're doing. Most of the info
here is given by various IDE tooling (which in the case of VS Code is configured
to use the same configs as the CLI tooling). But the one produced by `fast-lint`
is both complete and authoritative.

We aim to keep this under 30 seconds.

## Fixing Issues

Run `make fix-style` to fix many linting issues.

### Integration Tests

Jupiter has a large battery of integration tests that look at all aspects of the
application and its functionality, typically on the happy paths.

To run these specifically you can use `./scripts/run-itests.sh`. A typical invocation
might be:

`./scripts/run-itests.sh dev -k my_test_prefix`

This starts a distinct dev feature environment and opens a browser intstrumented for
testing. You'll see a typical test result from this one.

Tests are written in `Python` with `pytest` and `playwright`.

## Releases

Jupiter has a notion of versions, represented by releases. These mark specific
code versions, and the associated "release entities" for them (typically packaged apps).

The main Jupiter system has a continuous deployment release model. Every piece
of work that gets created via `./scripts/work/new-feature|new-bugfix` triggers a
a release to production - `webui` and `webapi` and `docs` and the others are thus
handled. Ditto, every PR also is pushed immediately to a staging environment.

Other sorts of artifacts - the `cli` and `desktop` apps (and in the future, the
`ios`, `android`, `linux`, etc. ones) have a coarser grained release process,
marked by releases.

Releases are named in semver fashion. We are currently at `v1.x.x` and plan
on staying on major `1` for a long time.

In terms of representation:

* On Git/GitHub, releases are marked by tags of the form `vx.y.x`.
* Ditto, the `master` branch is built such that it has one PR for each release.
  The `develop` branch tracks incremental releases of features and bugfixes.
* GitHub Releases are used to hold the artefacts produced by each release
  (source code, app packages).
* Releases can imply an app store upload too, but not necessarily. The platform
  apps are built with Electron and are thin shells around the web app. So the
  need for updating them, even as infrequent as releases isn't as big.

In terms of working:

* To create a release use `./scripts/release/new.sh x.y.z`.
* You'll need to edit `src/docs/material/releases/release-x.y.z.md` with the
  release notes. And update `mkdocs.yaml` to include it.
* Also run a `make stats-for-nerds` to include some per-release info.
* Then run `./scripts/release/finish.sh` to finish everything about the
  release on GitHub size.
* You can run `./scripts/build/desktop.sh` to build the new version of the
  desktop apps.
* And then `./scripts/release/gh-release.sh x.y.z` to create a new release
  on GitHub.
* Finally, if you so with you can upload to the AppStore via
  `./scripts/release/appstore-upload.sh x.y.z`. As mentioned above, not
  always necessary.

We'll work to unify these more in the future, but for now they're manual
operations that you can chose to do or not do.

For humans, these are useful too. The documentation has links to release notes,
which are useful for folks.