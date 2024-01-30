import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  FormControl,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  Stack,
} from "@mui/material";
import type { ActionArgs, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import {
  ShouldRevalidateFunction,
  useActionData,
  useTransition,
} from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { ApiError, Project, WorkspaceFeature } from "jupiter-gen";
import { useContext } from "react";
import { z } from "zod";
import { parseForm } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { WorkspaceFeatureFlagsEditor } from "~/components/feature-flags-editor";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { getIntent } from "~/logic/intent";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

const WorkspaceSettingsFormSchema = {
  intent: z.string(),
  name: z.string(),
  defaultProject: z.string(),
  featureFlags: z.array(z.nativeEnum(WorkspaceFeature)),
};

export const handle = {
  displayType: DisplayType.TOOL,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const summaryResponse = await getLoggedInApiClient(
    session
  ).getSummaries.getSummaries({
    include_default_project: true,
    include_projects: true,
  });
  const result = await getLoggedInApiClient(session).workspace.loadWorkspace(
    {}
  );

  return json({
    workspace: result.workspace,
    defaultProject: summaryResponse.default_project as Project,
    allProjects: summaryResponse.projects as Array<Project>,
  });
}

export async function action({ request }: ActionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const form = await parseForm(request, WorkspaceSettingsFormSchema);

  const { intent } = getIntent<undefined>(form.intent);

  try {
    switch (intent) {
      case "update": {
        await getLoggedInApiClient(session).workspace.updateWorkspace({
          name: {
            should_change: true,
            value: { the_name: form.name },
          },
        });

        return redirect(`/workspace/settings`);
      }

      case "change-default-project": {
        await getLoggedInApiClient(
          session
        ).workspace.changeWorkspaceDefaultProject({
          default_project_ref_id: { the_id: form.defaultProject },
        });

        return redirect(`/workspace/settings`);
      }

      case "change-feature-flags": {
        await getLoggedInApiClient(
          session
        ).workspace.changeWorkspaceFeatureFlags({
          feature_flags: form.featureFlags,
        });

        return redirect(`/workspace/settings`);
      }

      default:
        throw new Response("Bad Intent", { status: 500 });
    }
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status === StatusCodes.UNPROCESSABLE_ENTITY
    ) {
      return json(validationErrorToUIErrorInfo(error.body, intent));
    }

    throw error;
  }
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Settings() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const globalProperties = useContext(GlobalPropertiesContext);
  const topLevelInfo = useContext(TopLevelInfoContext);

  const inputsEnabled = transition.state === "idle";

  return (
    <TrunkPanel returnLocation="/workspace">
      <ToolPanel>
        <Stack useFlexGap gap={2}>
          <Card>
            <GlobalError intent="update" actionResult={actionData} />

            <CardHeader title="General" />
            <CardContent>
              <Stack spacing={2} useFlexGap>
                <FormControl fullWidth>
                  <InputLabel id="name">Name</InputLabel>
                  <OutlinedInput
                    label="Name"
                    name="name"
                    readOnly={!inputsEnabled}
                    defaultValue={loaderData.workspace.name.the_name}
                  />
                  <FieldError actionResult={actionData} fieldName="/name" />
                </FormControl>
              </Stack>
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
                  Save
                </Button>
              </ButtonGroup>
            </CardActions>
          </Card>

          {isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.PROJECTS
          ) && (
            <Card>
              <GlobalError
                intent="change-default-project"
                actionResult={actionData}
              />
              <CardHeader title="Default Project" />
              <CardContent>
                <Stack spacing={2} useFlexGap>
                  <FormControl fullWidth>
                    <InputLabel id="defaultProject">Default Project</InputLabel>
                    <Select
                      labelId="defaultProject"
                      name="defaultProject"
                      readOnly={!inputsEnabled}
                      defaultValue={loaderData.defaultProject.ref_id.the_id}
                      label="Default Project"
                    >
                      {loaderData.allProjects.map((p) => (
                        <MenuItem key={p.ref_id.the_id} value={p.ref_id.the_id}>
                          {p.name.the_name}
                        </MenuItem>
                      ))}
                    </Select>
                    <FieldError
                      actionResult={actionData}
                      fieldName="/deafult_project_ref_id"
                    />
                  </FormControl>
                </Stack>
              </CardContent>

              <CardActions>
                <ButtonGroup>
                  <Button
                    variant="contained"
                    disabled={!inputsEnabled}
                    type="submit"
                    name="intent"
                    value="change-default-project"
                  >
                    Change Default Project
                  </Button>
                </ButtonGroup>
              </CardActions>
            </Card>
          )}
          {!isWorkspaceFeatureAvailable(
            topLevelInfo.workspace,
            WorkspaceFeature.PROJECTS
          ) && (
            <input
              type="hidden"
              name="defaultProject"
              value={loaderData.defaultProject.ref_id.the_id}
            />
          )}

          <Card>
            <GlobalError
              intent="change-feature-flags"
              actionResult={actionData}
            />

            <CardHeader title="Feature Flags" />

            <CardContent>
              <WorkspaceFeatureFlagsEditor
                name="featureFlags"
                inputsEnabled={inputsEnabled}
                featureFlagsControls={topLevelInfo.workspaceFeatureFlagControls}
                defaultFeatureFlags={loaderData.workspace.feature_flags}
                hosting={globalProperties.hosting}
              />
            </CardContent>

            <CardActions>
              <ButtonGroup>
                <Button
                  variant="contained"
                  disabled={!inputsEnabled}
                  type="submit"
                  name="intent"
                  value="change-feature-flags"
                >
                  Change Feature Flags
                </Button>
              </ButtonGroup>
            </CardActions>
          </Card>
        </Stack>
      </ToolPanel>
    </TrunkPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error updating the workspace! Please try again!`
);
