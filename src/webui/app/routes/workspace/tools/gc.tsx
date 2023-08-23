import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
} from "@mui/material";
import type { ActionArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import {
  ShouldRevalidateFunction,
  useActionData,
  useTransition,
} from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { ApiError, SyncTarget } from "jupiter-gen";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolCard } from "~/components/infra/tool-card";
import { SyncTargetSelect } from "~/components/sync-target-select";
import {
  noErrorNoData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { fixSelectOutputToEnum, selectZod } from "~/logic/select";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const GCFormSchema = {
  gcTargets: selectZod(z.nativeEnum(SyncTarget)),
};

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, GCFormSchema);

  try {
    await getLoggedInApiClient(session).gc.garbageCollect({
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
  const transition = useTransition();
  const actionData = useActionData<typeof action>();
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = transition.state === "idle";

  return (
    <ToolCard returnLocation="/workspace">
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
    </ToolCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error garbage collecting! Please try again!`
);
