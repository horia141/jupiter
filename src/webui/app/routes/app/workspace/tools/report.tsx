import type { ProjectSummary, ReportResult } from "@jupiter/webapi-client";
import { ApiError, RecurringTaskPeriod } from "@jupiter/webapi-client";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  FormLabel,
  InputLabel,
  OutlinedInput,
  Stack,
} from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { DateTime } from "luxon";
import { useContext, useState } from "react";
import { z } from "zod";
import { parseQuery } from "zodix";
import { FieldError, GlobalError } from "~/components/infra/errors";

import { getLoggedInApiClient } from "~/api-clients.server";
import { makeToolErrorBoundary } from "~/components/infra/error-boundary";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { PeriodSelect } from "~/components/period-select";
import { ShowReport } from "~/components/show-report";
import type { ActionResult } from "~/logic/action-result";
import {
  isNoErrorSomeData,
  noErrorSomeData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { oneLessThanPeriod } from "~/logic/domain/period";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { TopLevelInfoContext } from "~/top-level-context";

const QuerySchema = {
  today: z
    .string()
    .regex(/[0-9][0-9][0-9][0-9][-][0-9][0-9][-][0-9][0-9]/)
    .optional(),
  period: z.nativeEnum(RecurringTaskPeriod).optional(),
  breakdownPeriod: z
    .union([z.nativeEnum(RecurringTaskPeriod), z.literal("none")])
    .optional(),
};

export const handle = {
  displayType: DisplayType.TOOL,
};

export async function loader({ request }: LoaderArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const { today, period, breakdownPeriod } = parseQuery(request, QuerySchema);

  if (
    today === undefined ||
    period === undefined ||
    breakdownPeriod === undefined
  ) {
    return json(noErrorSomeData({ report: undefined }));
  }

  const summaryResponse = await apiClient.getSummaries.getSummaries({
    include_projects: true,
  });

  try {
    const reportResponse = await apiClient.application.report({
      today: today,
      period: period,
      breakdown_period:
        breakdownPeriod !== "none" ? breakdownPeriod : undefined,
    });

    return json(
      noErrorSomeData({
        allProjects: summaryResponse.projects as Array<ProjectSummary>,
        report: reportResponse,
      })
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

export default function Report() {
  const loaderData = useLoaderDataSafeForAnimation<
    typeof loader
  >() as ActionResult<{
    allProjects: Array<ProjectSummary> | undefined;
    report: ReportResult | undefined;
  }>;
  const transition = useTransition();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const isBigScreen = useBigScreen();

  const [period, setPeriod] = useState(RecurringTaskPeriod.MONTHLY);
  const [breakdownPeriod, setBreakdownPeriod] = useState<
    RecurringTaskPeriod | "none"
  >(RecurringTaskPeriod.WEEKLY);

  const inputsEnabled = transition.state === "idle";

  function handleChangePeriod(
    newPeriod: RecurringTaskPeriod | RecurringTaskPeriod[] | "none"
  ) {
    if (newPeriod === "none") {
      return;
    }
    if (Array.isArray(newPeriod)) {
      newPeriod = newPeriod[0];
    }
    setPeriod(newPeriod);
    if (newPeriod === RecurringTaskPeriod.DAILY) {
      setBreakdownPeriod("none");
    } else {
      setBreakdownPeriod(oneLessThanPeriod(newPeriod));
    }
  }

  function handleChangeBreakdownPeriod(
    newPeriod: RecurringTaskPeriod | RecurringTaskPeriod[] | "none"
  ) {
    if (Array.isArray(newPeriod)) {
      newPeriod = newPeriod[0];
    }
    setBreakdownPeriod(newPeriod);
  }

  return (
    <ToolPanel method="get">
      <Card>
        <GlobalError actionResult={loaderData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="today" shrink>
                Today
              </InputLabel>
              <OutlinedInput
                type="date"
                notched
                label="Today"
                name="today"
                defaultValue={
                  isNoErrorSomeData(loaderData)
                    ? loaderData.data.report?.period_result.today ??
                      DateTime.local({
                        zone: topLevelInfo.user.timezone,
                      }).toISODate()
                    : DateTime.local({
                        zone: topLevelInfo.user.timezone,
                      }).toISODate()
                }
                readOnly={!inputsEnabled}
              />

              <FieldError actionResult={loaderData} fieldName="/today" />
            </FormControl>

            <Stack
              spacing={2}
              useFlexGap
              direction={isBigScreen ? "row" : "column"}
            >
              <FormControl fullWidth>
                <FormLabel id="period">Period</FormLabel>
                <PeriodSelect
                  labelId="period"
                  label="Period"
                  name="period"
                  inputsEnabled={inputsEnabled}
                  value={period}
                  onChange={handleChangePeriod}
                />
                <FieldError actionResult={loaderData} fieldName="/status" />
              </FormControl>

              <FormControl fullWidth>
                <FormLabel id="breakdownPeriod">Breakdown Period</FormLabel>
                <PeriodSelect
                  labelId="breakdownPeriod"
                  label="Breakdown Period"
                  name="breakdownPeriod"
                  inputsEnabled={inputsEnabled}
                  allowNonePeriod
                  value={breakdownPeriod}
                  onChange={handleChangeBreakdownPeriod}
                />
                <FieldError
                  actionResult={loaderData}
                  fieldName="/breakdown_period"
                />
              </FormControl>
            </Stack>
          </Stack>
        </CardContent>

        <CardActions>
          <ButtonGroup>
            <Button variant="contained" disabled={!inputsEnabled} type="submit">
              Run Report
            </Button>
          </ButtonGroup>
        </CardActions>
      </Card>

      {isNoErrorSomeData(loaderData) &&
        loaderData.data.allProjects !== undefined &&
        loaderData.data.report !== undefined && (
          <ShowReport
            topLevelInfo={topLevelInfo}
            allProjects={loaderData.data.allProjects}
            report={loaderData.data.report.period_result}
          />
        )}
    </ToolPanel>
  );
}

export const ErrorBoundary = makeToolErrorBoundary(
  () => `There was an error running the report! Please try again!`
);
