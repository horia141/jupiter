import type { SmartListTag } from "@jupiter/webapi-client";
import { ApiError } from "@jupiter/webapi-client";
import ReorderIcon from "@mui/icons-material/Reorder";
import TagIcon from "@mui/icons-material/Tag";
import TuneIcon from "@mui/icons-material/Tune";
import { Button, ButtonGroup } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, Outlet, useFetcher, useParams } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients.server";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { EntityCard } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
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

const ParamsSchema = {
  id: z.string(),
};

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request, params }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  try {
    const response = await apiClient.smartLists.smartListLoad({
      ref_id: id,
      allow_archived: false,
    });

    return json({
      smartList: response.smart_list,
      smartListTags: response.smart_list_tags,
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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function SmartListViewTags() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();

  const shouldShowALeaf = useBranchNeedsToShowLeaf();

  const tagsByRefId: { [tag: string]: SmartListTag } = {};
  for (const tag of loaderData.smartListTags) {
    tagsByRefId[tag.ref_id] = tag;
  }

  const archiveTagFetch = useFetcher();
  const isBigScreen = useBigScreen();

  function archiveTag(tag: SmartListTag) {
    archiveTagFetch.submit(
      {
        intent: "archive",
        name: "NOT USED - FOR ARCHIVE ONLY",
      },
      {
        method: "post",
        action: `/workspace/smart-lists/${loaderData.smartList.ref_id}/tags/${tag.ref_id}`,
      }
    );
  }

  return (
    <BranchPanel
      key={`smart-list-${loaderData.smartList.ref_id}/tags`}
      createLocation={`/workspace/smart-lists/${loaderData.smartList.ref_id}/tags/new`}
      extraControls={[
        <Button
          key={loaderData.smartList.ref_id}
          variant="outlined"
          to={`/workspace/smart-lists/${loaderData.smartList.ref_id}/items/details`}
          component={Link}
          startIcon={<TuneIcon />}
        >
          {isBigScreen ? "Details" : ""}
        </Button>,

        <ButtonGroup key={loaderData.smartList.ref_id}>
          <Button
            variant="outlined"
            to={`/workspace/smart-lists/${loaderData.smartList.ref_id}/items`}
            component={Link}
            startIcon={<ReorderIcon />}
          >
            "Items"
          </Button>

          <Button variant="contained" startIcon={<TagIcon />}>
            "Tags"
          </Button>
        </ButtonGroup>,
      ]}
      returnLocation="/workspace/smart-lists"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
          {loaderData.smartListTags.map((tag) => (
            <EntityCard
              key={tag.ref_id}
              allowSwipe
              allowMarkNotDone
              onMarkNotDone={() => archiveTag(tag)}
            >
              <Link
                to={`/workspace/smart-lists/${loaderData.smartList.ref_id}/tags/${tag.ref_id}`}
                prefetch="none"
              >
                <SmartListTagTag tag={tag} />
              </Link>
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

export const CatchBoundary = makeCatchBoundary(
  () => `Could not find smart list #${useParams().id}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading smart list #${
      useParams().id
    }! Please try again!`
);
