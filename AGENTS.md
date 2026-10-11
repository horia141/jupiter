# AGENTS.md

## Cursor Cloud specific instructions

### Overview

Thrive (codenamed Jupiter) is a life planning tool with a monorepo containing:

| Service | Tech |
|---|---|
| **WebAPI** (backend) | Python/FastAPI, SQLite |
| **WebUI** (frontend) | TypeScript/React Router/React |
| **Published** (public pages) | TypeScript/React Router/React |
| **API** | Python/FastAPI |
| **MCP** | Python/FastAPI |
| **Docs** | Python/MkDocs |

### Tool versions

The project uses **mise** as its tool/task runner. Required tools: Python 3.13.0, Node 22.23.3, pnpm, uv. Activate mise in your shell with `eval "$(~/.local/bin/mise activate bash)"`.

### Installing dependencies

```bash
mise run install
mise run prepare
```

### Running services

Start all 6 services (WebAPI, API, MCP, WebUI, Published, Docs) via mise:

```bash
mise run run:srv --instance <instance-name>
```

Then open the browser to the running instance:

```bash
mise run run:web --instance <instance-name>
```

Check service status: `npx pm2 status`. Check logs: `tail .build-cache/run/<instance-name>/<service>.log`.

## Architecture decision records (ADRs)

Accepted architecture and product decisions live in [`docs/adrs/`](docs/adrs/). Each file is a numbered ADR (e.g. `0008.webapi-backend-blend-via-config-global.md`) with **Context**, **Decision**, and **Consequences**.

**When working on a task, read any ADR that matches the area you are changing** — especially for configuration, deployment blends, search/CRM indexing, auth, client generation, and cross-cutting conventions. Do not contradict an accepted ADR without updating it or adding a new ADR that supersedes it.

Current topics include (non-exhaustive; browse the directory):

| ADR | Topic |
|-----|--------|
| 0002 | Dev environment and mise tasks |
| 0004 | API and MCP |
| 0005 | Recording events |
| 0006 | Client-side instant search |
| 0007 | Search entity indexing and backfill |
| 0008 | WebAPI backend blend via `Config.global` |
| 0009 | Search index method version |
| 0010 | Entity publish mechanism (public sharing) |
| 0011 | Access control and authenticated sharing |
| 0012 | Undo/redo sessions and groups (proposed) |
| 0014 | Section filters live in the URL |
| 0015 | Shared shell for the desktop and mobile apps |

## Generating code

Whenever some model from the core package is changed, code on the
client-side needs to be updated too. This is achieved by running:

```bash
mise run generate-client-code
```

This is the **only** way to properly update the code in `gen`.
This script exits non-zero on failure — wait for the line Client code generation complete on stderr before considering it done

## Adding migrations

If you want to make changes to the database, generate a migration
scaffold with

```bash
mise run add-migration "The name of the migration"
```

This will generate a new file in src/core/migrations/sqlite/versions
and in src/core/migrations/postgres/versions,
link it in the sequence of migrations, and you can then edit it
there, based on the patterns established.

### Lint, fix & check commands

- Auto-fix: `mise run lint:fix`
- Lint check: `mise run lint:lint`
- Full check: `mise run check`

### Gotchas

- The `secrets/` directory is gitignored and must exist with a `Config.secrets` file (can be empty) before running services. It is sourced by `tasks/_common.sh`.
- The generated TS WebAPI client (`gen/ts/webapi-client`) must be compiled (handled by `mise run prepare`) before the WebUI can build/run.
