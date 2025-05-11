import { ApiError, HomeTabTarget } from "@jupiter/webapi-client";
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
  Outlet,
  ShouldRevalidateFunction,
  useActionData,
  useNavigation,
} from "@remix-run/react";
import { useContext } from "react";
import { Stack } from "@mui/material";
import { AnimatePresence } from "framer-motion";

import {
  DisplayType,
  useTrunkNeedsToShowBranch,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
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
import { DocsHelpSubject } from "~/components/infra/docs-help";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";
import { StandardDivider } from "~/components/infra/standard-divider";
import { EntityCard } from "~/components/infra/entity-card";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { TrunkPanel } from "~/components/infra/layout/trunk-panel";

const ParamsSchema = z.object({});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("update"),
  }),
]);

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);

  const homeConfigResponse = await apiClient.home.homeConfigLoad({});

  return json({
    homeConfig: homeConfigResponse.home_config,
    tabs: homeConfigResponse.tabs,
  });
}

export async function action({ request }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
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

  const shouldShowABranch = useTrunkNeedsToShowBranch();
  const shouldShowALeafToo = useTrunkNeedsToShowLeaf();

  const topLevelInfo = useContext(TopLevelInfoContext);
  const inputsEnabled = navigation.state === "idle";
  const isBigScreen = useBigScreen();

  return (
    <TrunkPanel
      key={"home/settings"}
      returnLocation="/app/workspace"
      createLocation="/app/workspace/home/settings/tabs/new"
    >
      <NestingAwareBlock
        branchForceHide={shouldShowABranch}
        shouldHide={shouldShowABranch || shouldShowALeafToo}
      >
        <GlobalError actionResult={actionData} />
        <Form method="post">
          <Stack spacing={2} useFlexGap>
            {loaderData.tabs.length === 0 && (
              <EntityNoNothingCard
                title="You Have To Start Somewhere"
                message="There are no tabs to show. You can create a new tab."
                newEntityLocations="/app/workspace/home/settings/tabs/new"
                helpSubject={DocsHelpSubject.HOME}
              />
            )}
          </Stack>
        </Form>
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </TrunkPanel>
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
