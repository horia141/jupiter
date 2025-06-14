import { ApiError } from "@jupiter/webapi-client";
import {
  FormControl,
  InputLabel,
  OutlinedInput,
  Stack,
} from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { ReasonPhrases, StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import { SectionCardNew } from "~/components/infra/section-card-new";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { aGlobalError, validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";
import { DateInputWithSuggestions } from "~/components/domain/core/date-input-with-suggestions";
import { getSuggestedDatesForBigPlanMilestoneDate } from "~/logic/domain/suggested-date";
import { BigPlanMilestoneSourceLink } from "~/components/domain/concept/big-plan/big-plan-milestone-source-link";

const ParamsSchema = z.object({
  id: z.string(),
  milestoneId: z.string(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    name: z.string(),
    date: z.string(),
  }),
  z.object({
    intent: z.literal("archive"),
  }),
  z.object({
    intent: z.literal("remove"),
  }),
]);

export const handle = {
  displayType: DisplayType.LEAFLET,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { milestoneId } = parseParams(params, ParamsSchema);

  try {
    const result = await apiClient.milestones.bigPlanMilestoneLoad({
      ref_id: milestoneId,
      allow_archived: true,
    });

    return json({
      milestone: result.big_plan_milestone,
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

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id: bigPlanId, milestoneId } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.milestones.bigPlanMilestoneUpdate({
          ref_id: milestoneId,
          name: {
            should_change: true,
            value: form.name,
          },
          date: {
            should_change: true,
            value: form.date,
          },
        });

        return redirect(`/app/workspace/big-plans/${bigPlanId}`);
      }

      case "archive": {
        await apiClient.milestones.bigPlanMilestoneArchive({
          ref_id: milestoneId,
        });
        return redirect(`/app/workspace/big-plans/${bigPlanId}`);
      }

      case "remove": {
        await apiClient.milestones.bigPlanMilestoneRemove({
          ref_id: milestoneId,
        });
        return redirect(`/app/workspace/big-plans/${bigPlanId}`);
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

    if (error instanceof ApiError && error.status === StatusCodes.CONFLICT) {
      return json(aGlobalError(error.body));
    }

    throw error;
  }
}

export const shouldRevalidate: ShouldRevalidateFunction = standardShouldRevalidate;

export default function BigPlanMilestoneView() {
  const { milestone } = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = navigation.state === "idle" && !milestone.archived;

  return (
    <LeafPanel
      isLeaflet
      key={`big-plan-milestone-${milestone.ref_id}`}
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={milestone.archived}
      returnLocation={`/app/workspace/big-plans/${milestone.big_plan_ref_id}`}
    >
      <SectionCardNew
        id="milestone-properties"
        title="Properties"
        actions={
          <SectionActions
            id="milestone-properties"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                text: "Save",
                value: "update",
                highlight: true,
              }),
            ]}
          />
        }
      >
        <GlobalError actionResult={actionData} />
        <Stack spacing={2} useFlexGap>
          <Stack direction="row" spacing={2}>
            <FormControl sx={{ flexGrow: 3 }}>
              <InputLabel id="name">Name</InputLabel>
              <OutlinedInput
              label="Name"
              name="name"
              readOnly={!inputsEnabled}
              defaultValue={milestone.name}
            />
              <FieldError actionResult={actionData} fieldName="/name" />
            </FormControl>
            <BigPlanMilestoneSourceLink bigPlanId={milestone.big_plan_ref_id} />
          </Stack>

          <FormControl fullWidth>
            <InputLabel id="date" shrink margin="dense">
              Date
            </InputLabel>
            <DateInputWithSuggestions
              name="date"
              label="date"
              inputsEnabled={inputsEnabled}
              defaultValue={milestone.date}
              suggestedDates={getSuggestedDatesForBigPlanMilestoneDate(topLevelInfo.today)}
            />
            <FieldError actionResult={actionData} fieldName="/date" />
          </FormControl>
        </Stack>
      </SectionCardNew>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "../../..",
  ParamsSchema,
  {
    notFound: (params) => `Could not find milestone #${params.milestoneId}!`,
    error: (params) =>
      `There was an error loading milestone #${params.milestoneId}! Please try again!`,
  },
);
