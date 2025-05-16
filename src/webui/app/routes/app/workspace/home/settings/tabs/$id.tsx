import type {
  HomeTab,
  HomeWidget,
  SmallScreenHomeTabWidgetPlacement,
} from "@jupiter/webapi-client";
import { ApiError, HomeTabTarget } from "@jupiter/webapi-client";
import { Box, Button, Stack } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link, Outlet, useNavigation } from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { z } from "zod";
import { parseForm, parseParams } from "zodix";
import TuneIcon from "@mui/icons-material/Tune";
import { StatusCodes } from "http-status-codes";

import { getLoggedInApiClient } from "~/api-clients.server";
import { EntityNoNothingCard } from "~/components/infra/entity-no-nothing-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeBranchErrorBoundary } from "~/components/infra/error-boundary";
import { BranchPanel } from "~/components/infra/layout/branch-panel";
import { NestingAwareBlock } from "~/components/infra/layout/nesting-aware-block";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import {
  DisplayType,
  useBranchNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";
import { DocsHelpSubject } from "~/components/infra/docs-help";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { widgetDimensionRows, widgetTypeName } from "~/logic/widget";

const ParamsSchema = z.object({
  id: z.string(),
});

const UpdateFormSchema = z.discriminatedUnion("intent", [
  z.object({
    intent: z.literal("archive"),
  }),
  z.object({
    intent: z.literal("remove"),
  }),
]);

export const handle = {
  displayType: DisplayType.BRANCH,
};

export async function loader({ request, params }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);

  const result = await apiClient.tab.homeTabLoad({
    ref_id: id,
    allow_archived: true,
  });

  return json(result);
}

export async function action({ request, params }: ActionFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { id } = parseParams(params, ParamsSchema);
  const form = await parseForm(request, UpdateFormSchema);

  try {
    switch (form.intent) {
      case "archive": {
        await apiClient.tab.homeTabArchive({
          ref_id: id,
        });

        return redirect(`/app/workspace/home/settings`);
      }

      case "remove": {
        await apiClient.tab.homeTabRemove({
          ref_id: id,
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

export default function HomeTab() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const shouldShowALeaf = useBranchNeedsToShowLeaf();
  const navigation = useNavigation();
  const inputsEnabled = navigation.state === "idle";

  return (
    <BranchPanel
      showArchiveAndRemoveButton
      inputsEnabled={inputsEnabled}
      entityArchived={loaderData.tab.archived}
      key={`home-tab-${loaderData.tab.ref_id}`}
      createLocation={`/app/workspace/home/settings/tabs/${loaderData.tab.ref_id}/widgets/new`}
      returnLocation="/app/workspace/home/settings"
      extraControls={[
        <Button
          key="home-tab-details"
          variant="outlined"
          to={`/app/workspace/home/settings/tabs/${loaderData.tab.ref_id}/details`}
          component={Link}
          startIcon={<TuneIcon />}
        >
          Details
        </Button>,
      ]}
    >
      <NestingAwareBlock shouldHide={shouldShowALeaf}>
        {loaderData.widgets.length === 0 && (
          <EntityNoNothingCard
            title="You Have To Start Somewhere"
            message="There are no widgets to show. You can create a new widget."
            newEntityLocations={`/app/workspace/home/settings/tabs/${loaderData.tab.ref_id}/widgets/new`}
            helpSubject={DocsHelpSubject.HOME}
          />
        )}

        <EntityStack>
          {loaderData.tab.target === HomeTabTarget.BIG_SCREEN && (
            <>A big screen widget</>
          )}

          {loaderData.tab.target === HomeTabTarget.SMALL_SCREEN && (
            <SmallScreenWidgetPlacement
              homeTab={loaderData.tab}
              widgets={loaderData.widgets}
            />
          )}
        </EntityStack>
      </NestingAwareBlock>

      <AnimatePresence mode="wait" initial={false}>
        <Outlet />
      </AnimatePresence>
    </BranchPanel>
  );
}

export const ErrorBoundary = makeBranchErrorBoundary(
  "/app/workspace/home/settings",
  ParamsSchema,
  {
    notFound: (params) => `Could not find tab #${params.id}!`,
    error: (params) =>
      `There was an error loading tab #${params.id}! Please try again!`,
  },
);

interface SmallScreenWidgetPlacementProps {
  homeTab: HomeTab;
  widgets: HomeWidget[];
}

function SmallScreenWidgetPlacement(props: SmallScreenWidgetPlacementProps) {
  const widgetPlacement = props.homeTab
    .widget_placement as SmallScreenHomeTabWidgetPlacement;
  const widgetByRefId = new Map(
    props.widgets.map((widget) => [widget.ref_id, widget]),
  );

  return (
    <Stack useFlexGap sx={{ alignItems: "center" }}>
      {widgetPlacement.matrix.map((row, rowIndex) => {
        if (row === null) {
          return (
            <NewWidgetButton
              key={rowIndex}
              homeTab={props.homeTab}
              row={rowIndex}
              col={0}
            />
          );
        }

        if (
          rowIndex > 0 &&
          widgetPlacement.matrix[rowIndex] ===
            widgetPlacement.matrix[rowIndex - 1]
        ) {
          return null;
        }

        const widget = widgetByRefId.get(row);

        return (
          <PlacedWidget
            key={rowIndex}
            widget={widget!}
            row={rowIndex}
            col={0}
          />
        );
      })}
    </Stack>
  );
}

interface NewWidgetButtonProps {
  homeTab: HomeTab;
  row: number;
  col: number;
}

function NewWidgetButton(props: NewWidgetButtonProps) {
  return (
    <Button
      component={Link}
      to={`/app/workspace/home/settings/tabs/${props.homeTab.ref_id}/widgets/new?row=${props.row}&col=${props.col}`}
      variant="outlined"
      sx={{
        width: "8rem",
        height: "8rem",
      }}
    >
      Add Widget
    </Button>
  );
}

interface PlacedWidgetProps {
  widget: HomeWidget;
  row: number;
  col: number;
}

function PlacedWidget(props: PlacedWidgetProps) {
  const heightInRem = widgetDimensionRows(props.widget.geometry.dimension) * 8;

  return (
    <Box
      sx={{
        width: "8rem",
        height: `${heightInRem}rem`,
        border: (theme) => `2px dotted ${theme.palette.primary.main}`,
        borderRadius: "0.5rem",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Link
        to={`/app/workspace/home/settings/tabs/${props.widget.home_tab_ref_id}/widgets/${props.widget.ref_id}`}
        style={{
          marginLeft: "0.5rem",
          marginRight: "0.5rem",
          textAlign: "center",
        }}
      >
        {widgetTypeName(props.widget.the_type)}
      </Link>
    </Box>
  );
}
