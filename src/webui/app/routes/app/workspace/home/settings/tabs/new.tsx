import { ApiError, HomeTabTarget } from "@jupiter/webapi-client";
import { FormControl, InputLabel, OutlinedInput, Stack } from "@mui/material";
import type { ActionFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { HomeTabTargetSelect } from "~/components/domain/application/home/home-tab-target-select";
import { makeLeafErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError } from "~/components/infra/errors";
import { IconSelector } from "~/components/infra/icon-selector";
import { LeafPanel } from "~/components/infra/layout/leaf-panel";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { SectionCardNew } from "~/components/infra/section-card-new";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const ParamsSchema = z.object({});

const CreateFormSchema = z.object({
  target: z.nativeEnum(HomeTabTarget),
  name: z.string(),
  icon: z.string().optional(),
});

export const handle = {
  displayType: DisplayType.LEAF,
};

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, CreateFormSchema);

  try {
    const result = await apiClient.tab.homeTabCreate({
      target: form.target,
      name: form.name,
      icon: form.icon,
    });

    return redirect(
      `/app/workspace/home/settings/tabs/${result.new_home_tab.ref_id}`,
    );
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

export default function NewTab() {
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const inputsEnabled = navigation.state === "idle";

  return (
    <LeafPanel
      key={"home/settings/tab/new"}
      returnLocation="/app/workspace/home/settings"
      inputsEnabled={inputsEnabled}
    >
      <SectionCardNew
        title="New Tab"
        actions={
          <SectionActions
            id="tab-create"
            topLevelInfo={topLevelInfo}
            inputsEnabled={inputsEnabled}
            actions={[
              ActionSingle({
                id: "tab-create",
                text: "Create",
                value: "create",
                disabled: !inputsEnabled,
                highlight: true,
              }),
            ]}
          />
        }
      >
        <Stack spacing={2} useFlexGap>
          <FormControl fullWidth>
            <InputLabel id="name">Name</InputLabel>
            <OutlinedInput
              label="Name"
              name="name"
              readOnly={!inputsEnabled}
              defaultValue={""}
            />
            <FieldError actionResult={actionData} fieldName="/name" />
          </FormControl>

          <FormControl fullWidth>
            <HomeTabTargetSelect
              name="target"
              defaultValue={HomeTabTarget.BIG_SCREEN}
              inputsEnabled={inputsEnabled}
            />
            <FieldError actionResult={actionData} fieldName="/target" />
          </FormControl>
          <FormControl fullWidth>
            <InputLabel id="icon">Icon</InputLabel>
            <IconSelector readOnly={!inputsEnabled} />
            <FieldError actionResult={actionData} fieldName="/icon" />
          </FormControl>
        </Stack>
      </SectionCardNew>
    </LeafPanel>
  );
}

export const ErrorBoundary = makeLeafErrorBoundary(
  "/app/workspace/home/settings",
  ParamsSchema,
  {
    notFound: () => `Could not find the tab!`,
    error: () => `There was an error creating the tab! Please try again!`,
  },
);
