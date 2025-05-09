import { ApiError } from "@jupiter/webapi-client";
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
import { Stack } from "@mui/material";

import { DisplayType } from "~/rendering/use-nested-entities";
import { getLoggedInApiClient } from "~/api-clients.server";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { TopLevelInfoContext } from "~/top-level-context";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { GlobalError } from "~/components/infra/errors";
import { makeBranchErrorBoundary } from "~/components/infra/error-boundary";
import { SectionCardNew } from "~/components/infra/section-card-new";
import {
  ActionSingle,
  SectionActions,
} from "~/components/infra/section-actions";
import { useBigScreen } from "~/rendering/use-big-screen";

const ParamsSchema = z.object({});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
  }),
]);

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);

  const homeConfigResponse = await apiClient.home.homeConfigLoad({});

  return json({
    homeConfig: homeConfigResponse.home_config,
  });
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "update": {
        await apiClient.home.homeConfigUpdate({});
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
          <Stack spacing={2} useFlexGap></Stack>
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
