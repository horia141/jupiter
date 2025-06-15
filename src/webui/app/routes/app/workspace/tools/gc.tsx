import { ApiError, SyncTarget } from "@jupiter/webapi-client";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  styled,
} from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { EntitySummaryLink } from "~/components/infra/entity-summary-link";
import { EventSourceTag } from "~/components/infra/event-source-tag";
import { EntityCard } from "~/components/infra/entity-card";
import { makeToolErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { StandardDivider } from "~/components/infra/standard-divider";
import { SyncTargetSelect } from "~/components/domain/core/sync-target-select";
import { SyncTargetTag } from "~/components/domain/core/sync-target-tag";
import { TimeDiffTag } from "~/components/domain/core/time-diff-tag";
import {
  noErrorNoData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { fixSelectOutputToEnum, selectZod } from "~/logic/select";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const GCFormSchema = z.object({
  gcTargets: selectZod(z.nativeEnum(SyncTarget)),
});

export const handle = {
  displayType: DisplayType.TOOL,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.gc.gcLoadRuns({});
  return json(response.entries);
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, GCFormSchema);

  try {
    await apiClient.gc.gcDo({
      gc_targets: fixSelectOutputToEnum<SyncTarget>(form.gcTargets),
    });

    return json(noErrorNoData());
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

export default function GC() {
  const entries = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = navigation.state === "idle";

  return (
    <ToolPanel>
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <FormControl fullWidth>
            <InputLabel id="gcTargets">Garbage Collect Targets</InputLabel>
            <SyncTargetSelect
              topLevelInfo={topLevelInfo}
              labelId="gcTargets"
              label="Garbage Collect Targets"
              name="gcTargets"
              readOnly={!inputsEnabled}
            />
            <FieldError actionResult={actionData} fieldName="/gc_targets" />
          </FormControl>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button
              variant="contained"
              disabled={!inputsEnabled}
              type="submit"
              name="intent"
              value="update"
            >
              Garbage Collect
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>

      <StandardDivider title="Garbage Collection" size="large" />

      {entries.map((entry) => {
        return (
          <Accordion key={entry.ref_id}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <AccordionHeader>
                Run from <EventSourceTag source={entry.source} />
                with {entry.entity_records.length} entities archived
                <TimeDiffTag
                  today={topLevelInfo.today}
                  labelPrefix="from"
                  collectionTime={entry.created_time}
                />
              </AccordionHeader>
            </AccordionSummary>

            <AccordionDetails>
              <GCTargetsSection>
                GC Targets:
                {entry.gc_targets.map((target) => (
                  <SyncTargetTag key={target} target={target} />
                ))}
              </GCTargetsSection>

              {entry.entity_records.map((record) => (
                <EntityCard key={record.ref_id}>
                  <EntitySummaryLink
                    today={topLevelInfo.today}
                    summary={record}
                  />
                </EntityCard>
              ))}
            </AccordionDetails>
          </Accordion>
        );
      })}
    </ToolPanel>
  );
}

export const ErrorBoundary = makeToolErrorBoundary(
  () => `There was an error garbage collecting! Please try again!`,
);

const AccordionHeader = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  gap: theme.spacing(1),
  flexWrap: "wrap",
}));

const GCTargetsSection = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  gap: theme.spacing(1),
  flexWrap: "wrap",
  paddingBottom: theme.spacing(1),
}));
