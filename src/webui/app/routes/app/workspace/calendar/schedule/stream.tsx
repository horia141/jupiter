import { Button } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, Outlet, useSearchParams } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeBranchErrorBoundary } from "~/components/infra/error-boundary";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { ScheduleStreamColorTag } from "~/components/schedule-stream-color-tag";
import { basicShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useBranchNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.stream.scheduleStreamFind({
    allow_archived: false,
    include_notes: false,
  });

  return json({
    entries: response.entries,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction = basicShouldRevalidate;

export default function ScheduleStreamViewAll() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const [query] = useSearchParams();

  const shouldShowALeaf = useBranchNeedsToShowLeaf();

  return (
    <BranchPanel
      key="calendar-schedule-stream"
      createLocation={`/app/workspace/calendar/schedule/stream/new?${query}`}
      returnLocation={`/app/workspace/calendar?${query}`}
      extraControls={[
        <Button
          key="mock"
          variant="outlined"
          to={`/app/workspace/calendar/schedule/stream/new-external?${query}`}
          component={Link}
        >
          New External
        </Button>,
      ]}
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
          {loaderData.entries.map((entry) => (
            <EntityCard
              entityId={`schedule-stream-${entry.schedule_stream.ref_id}`}
              key={`schedule-stream-${entry.schedule_stream.ref_id}`}
            >
              <EntityLink
                to={`/app/workspace/calendar/schedule/stream/${entry.schedule_stream.ref_id}?${query}`}
              >
                <EntityNameComponent name={entry.schedule_stream.name} />
                <ScheduleStreamColorTag color={entry.schedule_stream.color} />
              </EntityLink>
            </EntityCard>
          ))}
        </EntityStack>
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </BranchPanel>
  );
}

export const ErrorBoundary = makeBranchErrorBoundary(
  () => `/app/workspace/calendar?${useSearchParams()}`,
  {
    error: () => "There was an error loading time plan calendar streams!",
  },
);
