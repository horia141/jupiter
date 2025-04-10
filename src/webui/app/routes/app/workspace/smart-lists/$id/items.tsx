import type { SmartListTag } from "@jupiter/webapi-client";
import { ApiError } from "@jupiter/webapi-client";
import ReorderIcon from "@mui/icons-material/Reorder";
import TagIcon from "@mui/icons-material/Tag";
import TuneIcon from "@mui/icons-material/Tune";
import { Button, ButtonGroup } from "@mui/material";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, Outlet, useNavigation } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import Check from "~/components/check";
import { DocsHelpSubject } from "~/components/docs-help";
import { EntityNameComponent } from "~/components/entity-name";
import { EntityNoNothingCard } from "~/components/entity-no-nothing-card";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeBranchErrorBoundary } from "~/components/infra/error-boundary";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { SmartListTagTag } from "~/components/smart-list-tag-tag";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useBranchNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";

const ParamsSchema = z.object({
  id: z.string(),
});

const UpdateSchema = z.discriminatedUnion("intent", [
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

  try {
    const response = await apiClient.smartLists.smartListLoad({
      ref_id: id,
      allow_archived: true,
      allow_archived_items: false,
      allow_archived_tags: false,
    });

    return json({
      smartList: response.smart_list,
      smartListTags: response.smart_list_tags,
      smartListItems: response.smart_list_items,
    });
  } catch (error) {
    if (error instanceof ApiError && error.status === StatusCodes.NOT_FOUND) {
      throw new Response(ReasonPhrases.NOT_FOUND, {
        status: StatusCodes.NOT_FOUND,
        statusText: ReasonPhrases.NOT_FOUND,
      });
    }

    throw error;
  }
}

export async function action({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateSchema);

  switch (form.intent) {
    case "archive": {
      await apiClient.smartLists.smartListArchive({
        ref_id: id,
      });

      return redirect("/app/workspace/smart-lists");
    }

    case "remove": {
      await apiClient.smartLists.smartListRemove({
        ref_id: id,
      });

      return redirect("/app/workspace/smart-lists");
    }
  }
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function SmartListViewItems() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const navigation = useNavigation();

  const inputsEnabled =
    navigation.state === "idle" && !loaderData.smartList.archived;

  const shouldShowALeaf = useBranchNeedsToShowLeaf();

  const tagsByRefId: { [tag: string]: SmartListTag } = {};
  for (const tag of loaderData.smartListTags) {
    tagsByRefId[tag.ref_id] = tag;
  }

  const isBigScreen = useBigScreen();

  return (
    <BranchPanel
      key={`smart-list-${loaderData.smartList.ref_id}/items`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.smartList.archived}
      createLocation={`/app/workspace/smart-lists/${loaderData.smartList.ref_id}/items/new`}
      extraControls={[
        <Button
          key={loaderData.smartList.ref_id}
          variant="outlined"
          to={`/app/workspace/smart-lists/${loaderData.smartList.ref_id}/items/details`}
          component={Link}
          startIcon={<TuneIcon />}
        >
          {isBigScreen ? "Details" : ""}
        </Button>,
        <ButtonGroup key={loaderData.smartList.ref_id}>
          <Button variant="contained" startIcon={<ReorderIcon />}>
            Items
          </Button>

          <Button
            variant="outlined"
            to={`/app/workspace/smart-lists/${loaderData.smartList.ref_id}/tags`}
            startIcon={<TagIcon />}
            component={Link}
          >
            Tags
          </Button>
        </ButtonGroup>,
      ]}
      returnLocation="/app/workspace/smart-lists"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        {loaderData.smartListItems.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no items to show. You can create a new item."
            newEntityLocations={`/app/workspace/smart-lists/${loaderData.smartList.ref_id}/items/new`}
            helpSubject={DocsHelpSubject.SMART_LISTS}
          />
        )}

        <EntityStack>
          {loaderData.smartListItems.map((item) => (
            <EntityCard
              key={`smart-list-item-${item.ref_id}`}
              entityId={`smart-list-item-${item.ref_id}`}
            >
              <EntityLink
                to={`/app/workspace/smart-lists/${loaderData.smartList.ref_id}/items/${item.ref_id}`}
              >
                <EntityNameComponent name={item.name} />
                <Check isDone={item.is_done} />
                {item.tags_ref_id.map((tid) => (
                  <SmartListTagTag key={tid} tag={tagsByRefId[tid]} />
                ))}
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
  "/app/workspace/smart-lists",
  ParamsSchema,
  {
    notFound: (params) => `Could not find smart list #${params.id}!`,
    error: (params) =>
      `There was an error loading smart list #${params.id}! Please try again!`,
  },
);
