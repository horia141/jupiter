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
% source ./scripts/new-dev-session.sh
# Set everything up in the Python and Node settings
% ./scripts/new-feature work-on-something
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

> A note on using `./scripts/new-feature.sh`, `./scripts/new-bugfix.sh`, and other
counterparts: we want to keep hygene of the `main` branch to have a linear history of
features and bugfixes, ocassionally tagged with releases. To enforce these, there's no
straight coding on the `main` branch, and the helper scripts help you setup things
in the right way.

## Releases

Coming soon.