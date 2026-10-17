import type { RouteConfig } from "@react-router/dev/routes";
import { index, prefix, route } from "@react-router/dev/routes";
import { bigPlansRoutes } from "@jupiter/core/apps/big_plans/routes";
import { choresRoutes } from "@jupiter/core/apps/chores/routes";
import { docsRoutes } from "@jupiter/core/apps/docs/routes";
import { habitsRoutes } from "@jupiter/core/apps/habits/routes";
import { journalsRoutes } from "@jupiter/core/apps/journals/routes";
import { lifePlanRoutes } from "@jupiter/core/apps/life_plan/routes";
import { metricsRoutes } from "@jupiter/core/apps/metrics/routes";
import { prmRoutes } from "@jupiter/core/apps/prm/routes";
import { smartListsRoutes } from "@jupiter/core/apps/smart_lists/routes";
import { timePlansRoutes } from "@jupiter/core/apps/time_plans/routes";
import { todosRoutes } from "@jupiter/core/apps/todo/routes";
import { vacationsRoutes } from "@jupiter/core/apps/vacations/routes";
import { workingMemRoutes } from "@jupiter/core/apps/working_mem/routes";

// Every route this service serves. The apps bring their own lists from core;
// this file only decides where they hang in the url tree.
export default [
  route("apps-latest-versions", "routes/apps-latest-versions.tsx"),
  route("release-manifest", "routes/release-manifest.tsx"),
  route("test-manifest", "routes/test-manifest.tsx"),
  route("pwa-manifest", "routes/pwa-manifest.tsx"),
  route("frontdoor", "routes/frontdoor.tsx"),
  route("healthz", "routes/healthz.tsx"),
  index("routes/index.tsx"),
  route("app", "routes/app.tsx", [
    route(
      "lifecycle/init/google/create-or-login-user",
      "routes/app/lifecycle/init/google/create-or-login-user.tsx",
    ),
    route(
      "lifecycle/init/apple/create-or-login-user",
      "routes/app/lifecycle/init/apple/create-or-login-user.tsx",
    ),
    route(
      "lifecycle/util/local/show-recovery-token",
      "routes/app/lifecycle/util/local/show-recovery-token.tsx",
    ),
    route(
      "lifecycle/email-verification/verify",
      "routes/app/lifecycle/email-verification/verify.tsx",
    ),
    route(
      "lifecycle/util/local/reset-password",
      "routes/app/lifecycle/util/local/reset-password.tsx",
    ),
    route(
      "lifecycle/util/user-already-exists",
      "routes/app/lifecycle/util/user-already-exists.tsx",
    ),
    route(
      "public/schedule/export/:externalId",
      "routes/app/public/schedule/export/$externalId.tsx",
    ),
    route(
      "lifecycle/init/local/create-user",
      "routes/app/lifecycle/init/local/create-user.tsx",
    ),
    route(
      "lifecycle/init/create-workspace",
      "routes/app/lifecycle/init/create-workspace.tsx",
    ),
    route(
      "lifecycle/init/google/prepare",
      "routes/app/lifecycle/init/google/prepare.tsx",
    ),
    route(
      "lifecycle/init/google/ready",
      "routes/app/lifecycle/init/google/ready.tsx",
    ),
    route(
      "lifecycle/init/google/native",
      "routes/app/lifecycle/init/google/native.tsx",
    ),
    route(
      "lifecycle/init/apple/prepare",
      "routes/app/lifecycle/init/apple/prepare.tsx",
    ),
    route(
      "lifecycle/init/apple/ready",
      "routes/app/lifecycle/init/apple/ready.tsx",
    ),
    route(
      "lifecycle/init/apple/native",
      "routes/app/lifecycle/init/apple/native.tsx",
    ),
    route(
      "lifecycle/login/local/login",
      "routes/app/lifecycle/login/local/login.tsx",
    ),
    route("pick-server", "routes/app/pick-server.tsx"),
    route("lifecycle/logout", "routes/app/lifecycle/logout.tsx"),
    route("render-fix", "routes/app/render-fix.tsx"),
    route("workspace", "routes/app/workspace.tsx", [
      route(
        "core/access/get-access-for-entity",
        "routes/app/workspace/core/access/get-access-for-entity.tsx",
      ),
      route(
        "core/access/acknowledge-invite",
        "routes/app/workspace/core/access/acknowledge-invite.tsx",
      ),
      route(
        "infra/entity-mutation-history",
        "routes/app/workspace/infra/entity-mutation-history.tsx",
      ),
      route(
        "push-integrations/email-tasks",
        "routes/app/workspace/push-integrations/email-tasks.tsx",
        [
          route(
            ":id",
            "routes/app/workspace/push-integrations/email-tasks/$id.tsx",
          ),
        ],
      ),
      route(
        "push-integrations/slack-tasks",
        "routes/app/workspace/push-integrations/slack-tasks.tsx",
        [
          route(
            ":id",
            "routes/app/workspace/push-integrations/slack-tasks/$id.tsx",
          ),
        ],
      ),
      route(
        "core/access/search-for-user",
        "routes/app/workspace/core/access/search-for-user.tsx",
      ),
      route(
        "core/access/request-access",
        "routes/app/workspace/core/access/request-access.tsx",
      ),
      route(
        "core/access/accept-access",
        "routes/app/workspace/core/access/accept-access.tsx",
      ),
      route(
        "core/access/cancel-invite",
        "routes/app/workspace/core/access/cancel-invite.tsx",
      ),
      route(
        "core/access/reject-access",
        "routes/app/workspace/core/access/reject-access.tsx",
      ),
      route(
        "core/access/forget-grant",
        "routes/app/workspace/core/access/forget-grant.tsx",
      ),
      route(
        "core/access/remove-grant",
        "routes/app/workspace/core/access/remove-grant.tsx",
      ),
      route(
        "core/access/update-grant",
        "routes/app/workspace/core/access/update-grant.tsx",
      ),
      route(
        "core/search-instant",
        "routes/app/workspace/core/search-instant.tsx",
      ),
      route(
        "core/access/invite",
        "routes/app/workspace/core/access/invite.tsx",
      ),
      route(
        "core/collaboration",
        "routes/app/workspace/core/collaboration.tsx",
        [
          route(
            "requests/from-me/:id",
            "routes/app/workspace/core/collaboration/requests/from-me/$id.tsx",
          ),
          route(
            "grants/from-me/:id",
            "routes/app/workspace/core/collaboration/grants/from-me/$id.tsx",
          ),
          route(
            "requests/to-me/:id",
            "routes/app/workspace/core/collaboration/requests/to-me/$id.tsx",
          ),
          route(
            "grants/to-me/:id",
            "routes/app/workspace/core/collaboration/grants/to-me/$id.tsx",
          ),
          route(
            "invites/:id",
            "routes/app/workspace/core/collaboration/invites/$id.tsx",
          ),
        ],
      ),
      route("core/inbox-tasks", "routes/app/workspace/core/inbox-tasks.tsx", [
        route(
          "update-status-and-eisen",
          "routes/app/workspace/core/inbox-tasks/update-status-and-eisen.tsx",
        ),
        route(":id", "routes/app/workspace/core/inbox-tasks/$id.tsx"),
      ]),
      route("mutation-history", "routes/app/workspace/mutation-history.tsx", [
        route(":id", "routes/app/workspace/mutation-history/$id.tsx"),
      ]),
      route("core/locations", "routes/app/workspace/core/locations.tsx", [
        route(
          "create-from-candidate",
          "routes/app/workspace/core/locations/create-from-candidate.tsx",
        ),
        route(
          "upsert-from-candidate",
          "routes/app/workspace/core/locations/upsert-from-candidate.tsx",
        ),
        route(
          "upsert-locations",
          "routes/app/workspace/core/locations/upsert-locations.tsx",
        ),
        route(
          "search-instant",
          "routes/app/workspace/core/locations/search-instant.tsx",
        ),
        route(":id", "routes/app/workspace/core/locations/$id.tsx"),
        route("new", "routes/app/workspace/core/locations/new.tsx"),
      ]),
      route("core/contacts", "routes/app/workspace/core/contacts.tsx", [
        route(
          "upsert-contacts",
          "routes/app/workspace/core/contacts/upsert-contacts.tsx",
        ),
        route(":id", "routes/app/workspace/core/contacts/$id.tsx"),
        route("new", "routes/app/workspace/core/contacts/new.tsx"),
      ]),
      route("home/settings", "routes/app/workspace/home/settings.tsx", [
        route("tabs/:id", "routes/app/workspace/home/settings/tabs/$id.tsx", [
          route(
            "widgets/:widgetId",
            "routes/app/workspace/home/settings/tabs/$id/widgets/$widgetId.tsx",
          ),
          route(
            "widgets/new",
            "routes/app/workspace/home/settings/tabs/$id/widgets/new.tsx",
          ),
          route(
            "details",
            "routes/app/workspace/home/settings/tabs/$id/details.tsx",
          ),
        ]),
        route("tabs/new", "routes/app/workspace/home/settings/tabs/new.tsx"),
      ]),
      route("core/publish", "routes/app/workspace/core/publish.tsx", [
        route(
          ":publishEntityId",
          "routes/app/workspace/core/publish/$publishEntityId.tsx",
        ),
      ]),
      route("gamification", "routes/app/workspace/gamification.tsx"),
      route("core/notes", "routes/app/workspace/core/notes.tsx", [
        route("update", "routes/app/workspace/core/notes/update.tsx"),
        route(":id", "routes/app/workspace/core/notes/$id.tsx"),
      ]),
      route("manage-api", "routes/app/workspace/manage-api.tsx", [
        route(":id", "routes/app/workspace/manage-api/$id.tsx"),
        route("new", "routes/app/workspace/manage-api/new.tsx"),
      ]),
      route("manage-mcp", "routes/app/workspace/manage-mcp.tsx", [
        route(":id", "routes/app/workspace/manage-mcp/$id.tsx"),
        route("new", "routes/app/workspace/manage-mcp/new.tsx"),
      ]),
      route("core/tags", "routes/app/workspace/core/tags.tsx", [
        route("upsert-tags", "routes/app/workspace/core/tags/upsert-tags.tsx"),
        route(":id", "routes/app/workspace/core/tags/$id.tsx"),
        route("new", "routes/app/workspace/core/tags/new.tsx"),
      ]),
      route("calendar", "routes/app/workspace/calendar.tsx", [
        route(
          "time-event/in-day-block/new-for-time-plan-activity",
          "routes/app/workspace/calendar/time-event/in-day-block/new-for-time-plan-activity.tsx",
        ),
        route(
          "time-event/in-day-block/new-for-chore-stack",
          "routes/app/workspace/calendar/time-event/in-day-block/new-for-chore-stack.tsx",
        ),
        route(
          "time-event/in-day-block/new-for-habit-stack",
          "routes/app/workspace/calendar/time-event/in-day-block/new-for-habit-stack.tsx",
        ),
        route(
          "time-event/in-day-block/new-for-todo-task",
          "routes/app/workspace/calendar/time-event/in-day-block/new-for-todo-task.tsx",
        ),
        route(
          "time-event/in-day-block/new-for-big-plan",
          "routes/app/workspace/calendar/time-event/in-day-block/new-for-big-plan.tsx",
        ),
        route(
          "time-event/in-day-block/new-for-chore",
          "routes/app/workspace/calendar/time-event/in-day-block/new-for-chore.tsx",
        ),
        route(
          "time-event/in-day-block/new-for-habit",
          "routes/app/workspace/calendar/time-event/in-day-block/new-for-habit.tsx",
        ),
        route(
          "time-event/full-days-block/:id",
          "routes/app/workspace/calendar/time-event/full-days-block/$id.tsx",
        ),
        route(
          "schedule/event-full-days/:id",
          "routes/app/workspace/calendar/schedule/event-full-days/$id.tsx",
        ),
        route(
          "schedule/event-full-days/new",
          "routes/app/workspace/calendar/schedule/event-full-days/new.tsx",
        ),
        route(
          "time-event/in-day-block/:id",
          "routes/app/workspace/calendar/time-event/in-day-block/$id.tsx",
        ),
        route(
          "schedule/event-in-day/:id",
          "routes/app/workspace/calendar/schedule/event-in-day/$id.tsx",
        ),
        route(
          "schedule/event-in-day/new",
          "routes/app/workspace/calendar/schedule/event-in-day/new.tsx",
        ),
        route(
          "schedule/export",
          "routes/app/workspace/calendar/schedule/export.tsx",
          [
            route(
              ":id",
              "routes/app/workspace/calendar/schedule/export/$id.tsx",
            ),
            route(
              "new",
              "routes/app/workspace/calendar/schedule/export/new.tsx",
            ),
          ],
        ),
        route(
          "schedule/stream",
          "routes/app/workspace/calendar/schedule/stream.tsx",
          [
            route(
              "new-external",
              "routes/app/workspace/calendar/schedule/stream/new-external.tsx",
            ),
            route(
              ":id",
              "routes/app/workspace/calendar/schedule/stream/$id.tsx",
            ),
            route(
              "new",
              "routes/app/workspace/calendar/schedule/stream/new.tsx",
            ),
          ],
        ),
        route("reschedule", "routes/app/workspace/calendar/reschedule.tsx"),
        route("settings", "routes/app/workspace/calendar/settings.tsx"),
      ]),
      route("security", "routes/app/workspace/security.tsx"),
      route("settings", "routes/app/workspace/settings.tsx"),
      route("account", "routes/app/workspace/account.tsx", [
        route("api-key/:id", "routes/app/workspace/account/api-key/$id.tsx"),
        route("api-key/new", "routes/app/workspace/account/api-key/new.tsx"),
        route("mcp-key/:id", "routes/app/workspace/account/mcp-key/$id.tsx"),
        route("mcp-key/new", "routes/app/workspace/account/mcp-key/new.tsx"),
      ]),
      index("routes/app/workspace/index.tsx"),
      route("tools", "routes/app/workspace/tools.tsx", [
        route("pomodoro", "routes/app/workspace/tools/pomodoro.tsx"),
        route("report", "routes/app/workspace/tools/report.tsx"),
        route("stats", "routes/app/workspace/tools/stats.tsx"),
        route("gen", "routes/app/workspace/tools/gen.tsx"),
        route("gc", "routes/app/workspace/tools/gc.tsx"),
      ]),
      ...prefix("apps", bigPlansRoutes),
      ...prefix("apps", choresRoutes),
      ...prefix("apps", docsRoutes),
      ...prefix("apps", habitsRoutes),
      ...prefix("apps", journalsRoutes),
      ...prefix("apps", lifePlanRoutes),
      ...prefix("apps", metricsRoutes),
      ...prefix("apps", prmRoutes),
      ...prefix("apps", smartListsRoutes),
      ...prefix("apps", timePlansRoutes),
      ...prefix("apps", todosRoutes),
      ...prefix("apps", vacationsRoutes),
      ...prefix("apps", workingMemRoutes),
    ]),
    index("routes/app/index.tsx"),
  ]),
] satisfies RouteConfig;
