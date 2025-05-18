import type {
  BigScreenHomeTabWidgetPlacement,
  HomeTab,
  HomeWidget,
  SmallScreenHomeTabWidgetPlacement,
} from "@jupiter/webapi-client";
import { ApiError, HomeTabTarget } from "@jupiter/webapi-client";
import { Box, Button, Stack, useTheme } from "@mui/material";
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import {
  useParams,
  Link,
  Outlet,
  useLocation,
  useNavigation,
  useSearchParams,
} from "@remix-run/react";
import { AnimatePresence } from "framer-motion";
import { z } from "zod";
import { parseForm, parseParams, parseQuery, parseQuerySafe } from "zodix";
import TuneIcon from "@mui/icons-material/Tune";
import { StatusCodes } from "http-status-codes";
import { Fragment } from "react";

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
import {
  isWidgetDimensionKSized,
  widgetDimensionCols,
  widgetDimensionRows,
  widgetTypeName,
} from "~/logic/widget";
import { newURLParams } from "~/logic/domain/navigation";
import { useBigScreen } from "~/rendering/use-big-screen";

enum Action {
  ADD_WIDGET = "add",
  MOVE_WIDGET = "move",
}

const ParamsSchema = z.object({
  id: z.string(),
});

const QuerySchema = z.object({
  action: z.nativeEnum(Action),
  row: z.coerce.number().optional(),
  col: z.coerce.number().optional(),
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
  const url = new URL(request.url);
  const query = parseQuerySafe(request, QuerySchema);

  if (query.error) {
    url.searchParams.set("action", Action.ADD_WIDGET);
    return redirect(url.pathname + url.search);
  }

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
  const [queryRaw] = useSearchParams();
  const query = parseQuery(queryRaw, QuerySchema);

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
            <BigScreenWidgetPlacement
              action={query.action}
              homeTab={loaderData.tab}
              widgets={loaderData.widgets}
            />
          )}

          {loaderData.tab.target === HomeTabTarget.SMALL_SCREEN && (
            <SmallScreenWidgetPlacement
              action={query.action}
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

interface BigScreenWidgetPlacementProps {
  action: Action;
  homeTab: HomeTab;
  widgets: HomeWidget[];
}

function BigScreenWidgetPlacement(props: BigScreenWidgetPlacementProps) {
  const widgetPlacement = props.homeTab
    .widget_placement as BigScreenHomeTabWidgetPlacement;
  const widgetByRefId = new Map(
    props.widgets.map((widget) => [widget.ref_id, widget]),
  );

  const isBigScreen = useBigScreen();
  const maxCols = widgetPlacement.matrix.length;
  const maxRows = widgetPlacement.matrix[0].length;

  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns: `repeat(${maxCols}, ${isBigScreen ? "8rem" : "1fr"})`,
        gridTemplateRows: `repeat(${maxRows}, 3rem)`,
        gridGap: "0.25rem",
        alignItems: "center",
        marginLeft: isBigScreen ? "auto" : undefined,
        marginRight: isBigScreen ? "auto" : undefined,
      }}
    >
      {Array.from({ length: maxRows }, (_, rowIndex) => {
        return (
          <Fragment key={rowIndex}>
            {Array.from({ length: maxCols }, (_, colIndex) => {
              const cell = widgetPlacement.matrix[colIndex][rowIndex];

              if (cell === null) {
                // Check if there's a k-sized widget before this row
                for (let i = 0; i < rowIndex; i++) {
                  const prevWidgetId = widgetPlacement.matrix[colIndex][i];
                  if (prevWidgetId !== null) {
                    const prevWidget = widgetByRefId.get(prevWidgetId);
                    if (
                      prevWidget &&
                      isWidgetDimensionKSized(prevWidget.geometry.dimension)
                    ) {
                      return null;
                    }
                  }
                }

                switch (props.action) {
                  case Action.ADD_WIDGET:
                    return (
                      <Box
                        key={`${rowIndex}-${colIndex}`}
                        sx={{
                          display: "flex",
                          gridRowStart: rowIndex + 1,
                          gridColumnStart: colIndex + 1,
                        }}
                      >
                        <NewWidgetButton
                          key={`${rowIndex}-${colIndex}`}
                          homeTab={props.homeTab}
                          row={rowIndex}
                          col={colIndex}
                        />
                      </Box>
                    );
                  case Action.MOVE_WIDGET:
                    return (
                      <Box
                        key={`${rowIndex}-${colIndex}`}
                        sx={{
                          display: "flex",
                          gridRowStart: rowIndex + 1,
                          gridColumnStart: colIndex + 1,
                        }}
                      >
                        <MoveWidgetButton
                          key={`${rowIndex}-${colIndex}`}
                          row={rowIndex}
                          col={colIndex}
                        />
                      </Box>
                    );
                }
              }

              // If the previous widget is the same as the current one, don't render the current block,
              // since this is a bigger widget that is taking up the space of the smaller one.
              // We check both the row and the column to make sure we don't render the same widget twice.
              if (
                rowIndex > 0 &&
                widgetPlacement.matrix[colIndex][rowIndex] ===
                  widgetPlacement.matrix[colIndex][rowIndex - 1]
              ) {
                return null;
              }

              if (
                colIndex > 0 &&
                widgetPlacement.matrix[colIndex][rowIndex] ===
                  widgetPlacement.matrix[colIndex - 1][rowIndex]
              ) {
                return null;
              }

              const widget = widgetByRefId.get(cell);

              return (
                <Box
                  key={`${rowIndex}-${colIndex}`}
                  sx={{
                    display: "flex",
                    gridRowStart: rowIndex + 1,
                    gridRowEnd:
                      rowIndex +
                      1 +
                      widgetDimensionRows(widget!.geometry.dimension),
                    gridColumnStart: colIndex + 1,
                    gridColumnEnd:
                      colIndex +
                      1 +
                      widgetDimensionCols(widget!.geometry.dimension),
                  }}
                >
                  <PlacedWidget
                    widget={widget!}
                    row={rowIndex}
                    col={colIndex}
                  />
                </Box>
              );
            })}
          </Fragment>
        );
      })}
    </Box>
  );
}

interface SmallScreenWidgetPlacementProps {
  action: Action;
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
          // Check if there's a k-sized widget before this row
          for (let i = 0; i < rowIndex; i++) {
            const prevWidgetId = widgetPlacement.matrix[i];
            if (prevWidgetId !== null) {
              const prevWidget = widgetByRefId.get(prevWidgetId);
              if (
                prevWidget &&
                isWidgetDimensionKSized(prevWidget.geometry.dimension)
              ) {
                return null;
              }
            }
          }

          switch (props.action) {
            case Action.ADD_WIDGET:
              return (
                <Box sx={{ width: "8rem" }} key={rowIndex}>
                  <NewWidgetButton
                    homeTab={props.homeTab}
                    row={rowIndex}
                    col={0}
                  />
                </Box>
              );
            case Action.MOVE_WIDGET:
              return (
                <Box sx={{ width: "8rem" }} key={rowIndex}>
                  <MoveWidgetButton
                    key={rowIndex}
                    row={rowIndex}
                    col={0}
                  />
                </Box>
              );
          }
        }

        // If the previous widget is the same as the current one, don't render the current block,
        // since this is a bigger widget that is taking up the space of the smaller one.
        if (
          rowIndex > 0 &&
          widgetPlacement.matrix[rowIndex] ===
            widgetPlacement.matrix[rowIndex - 1]
        ) {
          return null;
        }

        const widget = widgetByRefId.get(row);

        return (
          <Box sx={{ width: "8rem" }} key={rowIndex}>
            <PlacedWidget
              widget={widget!}
              row={rowIndex}
              col={0}
            />
          </Box>
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
  const [queryRaw] = useSearchParams();
  const query = parseQuery(queryRaw, QuerySchema);

  return (
    <Button
      component={Link}
      to={`/app/workspace/home/settings/tabs/${props.homeTab.ref_id}/widgets/new?${newURLParams(queryRaw, "row", props.row.toString(), "col", props.col.toString())}`}
      variant="outlined"
      sx={{
        color: (theme) =>
          query.row === props.row && query.col === props.col
            ? theme.palette.primary.contrastText
            : theme.palette.primary.main,
        backgroundColor: (theme) =>
          query.row === props.row && query.col === props.col
            ? theme.palette.primary.light
            : "transparent",
        width: "100%",
        height: "3rem",
      }}
    >
      Add
    </Button>
  );
}

interface MoveWidgetButtonProps {
  row: number;
  col: number;
}

function MoveWidgetButton(props: MoveWidgetButtonProps) {
  const location = useLocation();
  const [queryRaw] = useSearchParams();
  const query = parseQuery(queryRaw, QuerySchema);
  const shouldHighlight = query.row === props.row && query.col === props.col;

  return (
    <Button
      component={Link}
      to={`${location.pathname}?${newURLParams(queryRaw, "row", props.row.toString(), "col", props.col.toString())}`}
      variant="outlined"
      sx={{
        color: (theme) =>
          shouldHighlight
            ? theme.palette.primary.contrastText
            : theme.palette.primary.main,
        backgroundColor: (theme) =>
          shouldHighlight ? theme.palette.primary.light : "transparent",
        width: "100%",
        height: "3rem",
      }}
    >
      Move
    </Button>
  );
}

interface PlacedWidgetProps {
  widget: HomeWidget;
  row: number;
  col: number;
}

function PlacedWidget(props: PlacedWidgetProps) {
  const heightInRem = widgetDimensionRows(props.widget.geometry.dimension) * 3;
  const widthInRem = widgetDimensionCols(props.widget.geometry.dimension) * 8;
  const { widgetId } = useParams();
  const isBigScreen = useBigScreen();
  const shouldHighlight = widgetId === props.widget.ref_id;
  const theme = useTheme();

  return (
    <Box
      sx={{
        fontSize: "0.64rem",
        height: `${heightInRem}rem`,
        width: "100%",
        minWidth: isBigScreen ? `${widthInRem}rem` : undefined,
        border: (theme) => `2px dotted ${theme.palette.primary.main}`,
        borderRadius: "4px",
        borderBottomLeftRadius: isWidgetDimensionKSized(
          props.widget.geometry.dimension,
        )
          ? 0
          : "4px",
        borderBottomRightRadius: isWidgetDimensionKSized(
          props.widget.geometry.dimension,
        )
          ? 0
          : "4px",
        borderBottom: isWidgetDimensionKSized(props.widget.geometry.dimension)
          ? `4px dotted ${theme.palette.primary.main}`
          : `2px dotted ${theme.palette.primary.main}`,
        backgroundColor: shouldHighlight
          ? theme.palette.primary.light
          : "transparent",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Link
        to={`/app/workspace/home/settings/tabs/${props.widget.home_tab_ref_id}/widgets/${props.widget.ref_id}?action=${Action.MOVE_WIDGET}`}
        style={{
          marginLeft: "0.5rem",
          marginRight: "0.5rem",
          textAlign: "center",
          color: shouldHighlight
            ? theme.palette.primary.contrastText
            : theme.palette.primary.main,
        }}
      >
        {widgetTypeName(props.widget.the_type)}
      </Link>
    </Box>
  );
}
