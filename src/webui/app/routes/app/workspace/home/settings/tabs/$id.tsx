import type { HomeTab } from "@jupiter/webapi-client";
import { ApiError } from "@jupiter/webapi-client";
import { Button } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, Outlet, useNavigation } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import TuneIcon from "@mui/icons-material/Tune";
import { StatusCodes } from "http-status-codes";

import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNameComponent } from "~/components/infra/entity-name";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeBranchErrorBoundary } from "~/components/infra/error-boundary";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useBranchNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { DocsHelpSubject } from "~/components/infra/docs-help";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";

const ParamsSchema = z.object({
  id: z.string(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("archive"),
  }),
  z.object({
    intent: z.literal("remove"),
  }),
]);

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  const result = await apiClient.tab.homeTabLoad({
    ref_id: id,
    allow_archived: true,
  });

  return json(result);
}

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "archive": {
        await apiClient.tab.homeTabArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/home/settings`);
      }

      case "remove": {
        await apiClient.tab.homeTabRemove({
          ref_id: id,
        });

        return redirect(`/app/workspace/home/settings`);
      }

      default:
        throw new Response("Bad Intent", { status: 500 });
    }
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status === StatusCodes.UNPROCESSABLE_ENTITY
    ) {
      return json(validationErrorToUIErrorInfo(error.body));
    }

    throw error;
  }
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function HomeTab() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const shouldShowALeaf = useBranchNeedsToShowLeaf();
  const navigation = useNavigation();
  const inputsEnabled = navigation.state === "idle";

  return (
    <BranchPanel
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.tab.archived}
      key={`home-tab-${loaderData.tab.ref_id}`}
      createLocation={`/app/workspace/home/settings/tabs/${loaderData.tab.ref_id}/widgets/new`}
      returnLocation="/app/workspace/home/settings"
      extraControls={[
        <Button
          key="home-tab-details"
          variant="outlined"
          to={`/app/workspace/home/settings/tabs/${loaderData.tab.ref_id}/details`}
          component={Link}
          startIcon={<TuneIcon />}
        >
          Details
        </Button>,
      ]}
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        {loaderData.widgets.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no widgets to show. You can create a new widget."
            newEntityLocations={`/app/workspace/home/settings/tabs/${loaderData.tab.ref_id}/widgets/new`}
            helpSubject={DocsHelpSubject.HOME}
          />
        )}

        <EntityStack>
          {loaderData.widgets.map((widget) => (
            <EntityCard
              entityId={`home-widget-${widget.ref_id}`}
              key={`home-widget-${widget.ref_id}`}
            >
              <EntityLink
                to={`/app/workspace/home/settings/tabs/${loaderData.tab.ref_id}/widgets/${widget.ref_id}`}
              >
                <EntityNameComponent name={widget.name} />
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
  "/app/workspace/home/settings",
  ParamsSchema,
  {
    notFound: (params) => `Could not find tab #${params.id}!`,
    error: (params) =>
      `There was an error loading tab #${params.id}! Please try again!`,
  },
);
