import { Button, ButtonGroup } from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import { Link, ShouldRevalidateFunction, useFetcher, useOutlet, useParams } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import type { SmartListTag } from "jupiter-gen";
import { ApiError } from "jupiter-gen";
import { z } from "zod";
import { parseParams } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { ActionHeader } from "~/components/infra/actions-header";
import { BranchCard } from "~/components/infra/branch-card";
import { makeCatchBoundary } from "~/components/infra/catch-boundary";
import { EntityCard } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { LeafPanel } from "~/components/infra/leaf-panel";
import { NestingAwarePanel } from "~/components/infra/nesting-aware-panel";
import { SmartListTagTag } from "~/components/smart-list-tag-tag";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
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

export const shouldRevalidate: ShouldRevalidateFunction = standardShouldRevalidate;

export default function SmartListViewTags() {
  const outlet = useOutlet();
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
    <BranchCard key={`${loaderData.smartList.ref_id.the_id}/tags`}>
      <NestingAwarePanel showOutlet={shouldShowALeaf}>
        <ActionHeader returnLocation="/workspace">
          <ButtonGroup>
            <Button
              variant="contained"
              to={`/workspace/smart-lists/${loaderData.smartList.ref_id.the_id}/tags/new`}
              component={Link}
            >
              Create
            </Button>

            <Button
              variant="outlined"
              to={`/workspace/smart-lists/${loaderData.smartList.ref_id.the_id}/items/details`}
              component={Link}
            >
              Details
            </Button>
          </ButtonGroup>

          <ButtonGroup>
            <Button
              variant="outlined"
              to={`/workspace/smart-lists/${loaderData.smartList.ref_id.the_id}/items`}
              component={Link}
            >
              Items
            </Button>
            <Button variant="contained">Tags</Button>
          </ButtonGroup>
        </ActionHeader>

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
      </NestingAwarePanel>

      <LeafPanel show={shouldShowALeaf}>{outlet}</LeafPanel>
    </BranchCard>
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
