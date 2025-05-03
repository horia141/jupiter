import { ApiError, WorkspaceFeature } from "@jupiter/webapi-client";
import { z } from "zod";
import {
  ActionFunctionArgs,
  json,
  LoaderFunctionArgs,
  redirect,
} from "@remix-run/node";
import { parseForm } from "zodix";
import { StatusCodes } from "http-status-codes";
import {
  Form,
  ShouldRevalidateFunction,
  useActionData,
  useNavigation,
} from "@remix-run/react";
import { useContext } from "react";
import { FormControl, Stack } from "@mui/material";

import { DisplayType } from "~/rendering/use-nested-entities";
import { getLoggedInApiClient } from "~/api-clients.server";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { TopLevelInfoContext } from "~/top-level-context";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { makeBranchErrorBoundary } from "~/components/infra/error-boundary";
import { SectionCardNew } from "~/components/infra/section-card-new";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { HabitSelectSingle } from "~/components/domain/concept/habit/habit-select-single";
import { StandardDivider } from "~/components/infra/standard-divider";
import { useBigScreen } from "~/rendering/use-big-screen";

const ParamsSchema = z.object({});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
    keyHabit1: z.string().optional(),
    keyHabit2: z.string().optional(),
    keyHabit3: z.string().optional(),
  }),
]);

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
    include_habits: true,
    include_metrics: true,
  });
  const homeConfigResponse = await apiClient.home.homeConfigLoad({});

  return json({
    homeConfig: homeConfigResponse.home_config,
    allHabits: summaryResponse.habits || [],
    allProjects: summaryResponse.projects || [],
    allMetrics: summaryResponse.metrics || [],
  });
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        const keyHabits = [
          form.keyHabit1,
          form.keyHabit2,
          form.keyHabit3,
        ].filter(Boolean) as string[];
        await apiClient.home.homeConfigUpdate({
          key_habits: {
            should_change: true,
            value: keyHabits,
          },
          key_metrics: {
            should_change: false,
          },
        });
        return redirect(`/app/workspace/home/settings`);
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

    throw error;
  }
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function HomeSettings() {
  const navigation = useNavigation();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const actionData = useActionData<typeof action>();

  const topLevelInfo = useContext(TopLevelInfoContext);
  const inputsEnabled = navigation.state === "idle";
  const isBigScreen = useBigScreen();

  return (
    <BranchPanel
      key={"home/settings"}
      returnLocation="/app/workspace"
      inputsEnabled={inputsEnabled}
    >
      <Form method="post">
        <SectionCardNew
          id="home-settings"
          title="Settings"
          actions={
            <SectionActions
              id="home-settings-actions"
              topLevelInfo={topLevelInfo}
              inputsEnabled={inputsEnabled}
              actions={[
                ActionSingle({
                  id: "home-settings-save",
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
            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.HABITS,
            ) && (
              <>
                <StandardDivider title="Key Habits" size="large" />
                <Stack direction={isBigScreen ? "row" : "column"} spacing={2}>
                  <FormControl fullWidth>
                    <HabitSelectSingle
                      allowNone
                      name="keyHabit1"
                      label="Key Habit"
                      groupByProjects={isWorkspaceFeatureAvailable(
                        topLevelInfo.workspace,
                        WorkspaceFeature.PROJECTS,
                      )}
                      allProjects={loaderData.allProjects}
                      allHabits={loaderData.allHabits}
                      defaultValue={
                        loaderData.homeConfig.key_habits[0] ?? undefined
                      }
                    />
                    <FieldError
                      actionResult={actionData}
                      fieldName="/key_habits"
                    />
                  </FormControl>

                  <FormControl fullWidth>
                    <HabitSelectSingle
                      allowNone
                      name="keyHabit2"
                      label="Key Habit"
                      groupByProjects={isWorkspaceFeatureAvailable(
                        topLevelInfo.workspace,
                        WorkspaceFeature.PROJECTS,
                      )}
                      allProjects={loaderData.allProjects}
                      allHabits={loaderData.allHabits}
                      defaultValue={
                        loaderData.homeConfig.key_habits[1] ?? undefined
                      }
                    />
                    <FieldError
                      actionResult={actionData}
                      fieldName="/key_habits"
                    />
                  </FormControl>

                  <FormControl fullWidth>
                    <HabitSelectSingle
                      allowNone
                      name="keyHabit3"
                      label="Key Habit"
                      groupByProjects={isWorkspaceFeatureAvailable(
                        topLevelInfo.workspace,
                        WorkspaceFeature.PROJECTS,
                      )}
                      allProjects={loaderData.allProjects}
                      allHabits={loaderData.allHabits}
                      defaultValue={
                        loaderData.homeConfig.key_habits[2] ?? undefined
                      }
                    />
                    <FieldError
                      actionResult={actionData}
                      fieldName="/key_habits"
                    />
                  </FormControl>
                </Stack>
              </>
            )}
          </Stack>
        </SectionCardNew>
      </Form>
    </BranchPanel>
  );
}

export const ErrorBoundary = makeBranchErrorBoundary(
  "/app/workspace/home",
  ParamsSchema,
  {
    notFound: () => `Could not find the home settings!`,
    error: () =>
      `There was an error loading the home settings! Please try again!`,
  },
);
