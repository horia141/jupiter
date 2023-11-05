import ReorderIcon from "@mui/icons-material/Reorder";
import TagIcon from "@mui/icons-material/Tag";
import TuneIcon from "@mui/icons-material/Tune";
import { Button, ButtonGroup } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import {
  Link,
  Outlet,
  ShouldRevalidateFunction,
  useFetcher,
  useParams,
} from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import type { SmartListTag } from "jupiter-gen";
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
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
import { getSession } from "~/sessions";

const ParamsSchema = {
  id: z.string(),
};

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request, params }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { id } = parseParams(params, ParamsSchema);

  try {
    const response = await getLoggedInApiClient(
      session
    ).smartList.loadSmartList({
      ref_id: { the_id: id },
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
  const isBigScreen = useBigScreen();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();

  const shouldShowALeaf = useBranchNeedsToShowLeaf();

  const tagsByRefId: { [tag: string]: SmartListTag } = {};
  for (const tag of loaderData.smartListTags) {
    tagsByRefId[tag.ref_id.the_id] = tag;
  }

  const archiveTagFetch = useFetcher();

  function archiveTag(tag: SmartListTag) {
    archiveTagFetch.submit(
      {
        intent: "archive",
        name: "NOT USED - FOR ARCHIVE ONLY",
      },
      {
        method: "post",
        action: `/workspace/smart-lists/${loaderData.smartList.ref_id.the_id}/tags/${tag.ref_id.the_id}`,
      }
    );
  }

  return (
    <BranchPanel
      key={`${loaderData.smartList.ref_id.the_id}/tags`}
      createLocation={`/workspace/smart-lists/${loaderData.smartList.ref_id.the_id}/tags/new`}
      extraFilters={
        <ButtonGroup>
          {isBigScreen ? (
            <Button
              variant="outlined"
              to={`/workspace/smart-lists/${loaderData.smartList.ref_id.the_id}/items/details`}
              component={Link}
              startIcon={<TuneIcon />}
            >
              "Details"
            </Button>
          ) : (
            <Button
              variant="outlined"
              to={`/workspace/smart-lists/${loaderData.smartList.ref_id.the_id}/items/details`}
              component={Link}
            >
              <TuneIcon />
            </Button>
          )}

          {isBigScreen ? (
            <Button
              variant="outlined"
              to={`/workspace/smart-lists/${loaderData.smartList.ref_id.the_id}/items`}
              component={Link}
              startIcon={<ReorderIcon />}
            >
              "Items"
            </Button>
          ) : (
            <Button
              variant="outlined"
              to={`/workspace/smart-lists/${loaderData.smartList.ref_id.the_id}/items`}
              component={Link}
            >
              <ReorderIcon />
            </Button>
          )}

          {isBigScreen ? (
            <Button variant="contained" startIcon={<TagIcon />}>
              "Tags"
            </Button>
          ) : (
            <Button variant="contained">
              <TagIcon />
            </Button>
          )}
        </ButtonGroup>
      }
      returnLocation="/workspace/smart-lists"
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        <EntityStack>
          {loaderData.smartListTags.map((tag) => (
            <EntityCard
              key={tag.ref_id.the_id}
              allowSwipe
              allowMarkNotDone
              onMarkNotDone={() => archiveTag(tag)}
            >
              <Link
                to={`/workspace/smart-lists/${loaderData.smartList.ref_id.the_id}/tags/${tag.ref_id.the_id}`}
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
  () => `Could not find smart list #${useParams().key}!`
);

export const ErrorBoundary = makeErrorBoundary(
  () =>
    `There was an error loading smart list #${
      useParams().key
    }! Please try again!`
);
