import type { ProjectSummary } from "@jupiter/webapi-client";
import { ApiError, WorkspaceFeature } from "@jupiter/webapi-client";
import { FormControl } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useActionData, useNavigation } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeBranchErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { ProjectSelect } from "~/components/domain/concept/project/project-select";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";
import { SectionCard } from "~/components/infra/section-card";
import {
  SectionActions,
  ActionSingle,
} from "~/components/infra/section-actions";

const ParamsSchema = z.object({});

const UpdateFormSchema = z.object({
  project: z.string().optional(),
});

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
  });

  const personSettingsResponse = await apiClient.persons.personLoadSettings({});

  return json({
    catchUpProject: personSettingsResponse.catch_up_project,
    allProjects: summaryResponse.projects as Array<ProjectSummary>,
  });
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    if (form.project === undefined) {
      throw new Error("Invalid application state");
    }

    await apiClient.persons.personChangeCatchUpProject({
      catch_up_project_ref_id: form.project,
    });

    return redirect(`/app/workspace/persons/settings`);
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

export default function PersonsSettings() {
  const navigation = useNavigation();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();

  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = navigation.state === "idle";

  return (
    <BranchPanel
      key={"persons/settings"}
      returnLocation="/app/workspace/persons"
      inputsEnabled={inputsEnabled}
    >
      <GlobalError actionResult={actionData} />
      {isWorkspaceFeatureAvailable(
        topLevelInfo.workspace,
        WorkspaceFeature.PROJECTS,
      ) && (
        <SectionCard
          id="persons-settings"
          title="Catch Up Project"
          actions={
            <SectionActions
              id="persons-settings-actions"
              topLevelInfo={topLevelInfo}
              inputsEnabled={inputsEnabled}
              actions={[
                ActionSingle({
                  text: "Save",
                  value: "change",
                  highlight: true,
                }),
              ]}
            />
          }
        >
          <FormControl fullWidth>
            <ProjectSelect
              name="project"
              label="Catch Up Project"
              inputsEnabled={inputsEnabled}
              disabled={false}
              allProjects={loaderData.allProjects}
              defaultValue={loaderData.catchUpProject.ref_id}
            />
            <FieldError
              actionResult={actionData}
              fieldName="/catch_up_project_key"
            />
          </FormControl>
        </SectionCard>
      )}
    </BranchPanel>
  );
}

export const ErrorBoundary = makeBranchErrorBoundary(
  "/app/workspace/persons",
  ParamsSchema,
  {
    notFound: () => `Could not find the persons settings!`,
    error: () =>
      `There was an error loading the persons settings! Please try again!`,
  },
);
