import type { ProjectSummary, ReportResult } from "@jupiter/webapi-client";
import { ApiError, RecurringTaskPeriod } from "@jupiter/webapi-client";
import type { SelectChangeEvent } from "@mui/material";
import {
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
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

import { getLoggedInApiClient } from "~/api-clients";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { ShowReport } from "~/components/show-report";
import type { ActionResult } from "~/logic/action-result";
import {
  isNoErrorSomeData,
  noErrorSomeData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import {
  comparePeriods,
  oneLessThanPeriod,
  periodName,
} from "~/logic/domain/period";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
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
  const session = await getSession(request.headers.get("Cookie"));
  const { today, period, breakdownPeriod } = parseQuery(request, QuerySchema);

  if (
    today === undefined ||
    period === undefined ||
    breakdownPeriod === undefined
  ) {
    return json(noErrorSomeData({ report: undefined }));
  }

  const summaryResponse = await getLoggedInApiClient(
    session
  ).getSummaries.getSummaries({
    include_projects: true,
  });

  try {
    const reportResponse = await getLoggedInApiClient(
      session
    ).application.report({
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

  const [period, setPeriod] = useState(RecurringTaskPeriod.MONTHLY);
  const [breakdownPeriod, setBreakdownPeriod] = useState<
    RecurringTaskPeriod | "none"
  >(RecurringTaskPeriod.WEEKLY);

  const inputsEnabled = transition.state === "idle";

  function handleChangePeriod(event: SelectChangeEvent<RecurringTaskPeriod>) {
    const newPeriod = event.target.value as RecurringTaskPeriod;
    setPeriod(newPeriod);
    if (newPeriod === RecurringTaskPeriod.DAILY) {
      setBreakdownPeriod("none");
    } else {
      setBreakdownPeriod(oneLessThanPeriod(newPeriod));
    }
  }

  function handleChangeBreakdownPeriod(
    event: SelectChangeEvent<RecurringTaskPeriod | "none">
  ) {
    setBreakdownPeriod(event.target.value as RecurringTaskPeriod | "none");
  }

  return (
    <ToolPanel method="get">
      <Card>
        <GlobalError actionResult={loaderData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="today">Today</InputLabel>
              <OutlinedInput
                type="date"
                label="Today"
                name="today"
                defaultValue={
                  isNoErrorSomeData(loaderData)
                    ? loaderData.data.report?.period_result.today ??
                      DateTime.now().toISODate()
                    : DateTime.now().toISODate()
                }
                readOnly={!inputsEnabled}
              />

              <FieldError actionResult={loaderData} fieldName="/today" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="period">Period</InputLabel>
              <Select
                labelId="period"
                name="period"
                readOnly={!inputsEnabled}
                value={period}
                onChange={handleChangePeriod}
                label="Period"
              >
                {Object.values(RecurringTaskPeriod).map((s) => (
                  <MenuItem key={s} value={s}>
                    {periodName(s)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError actionResult={loaderData} fieldName="/status" />
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="breakdownPeriod">Breakdown Period</InputLabel>
              <Select
                labelId="breakdownPeriod"
                name="breakdownPeriod"
                readOnly={!inputsEnabled}
                value={breakdownPeriod}
                onChange={handleChangeBreakdownPeriod}
                label="Breakdown Period"
              >
                <MenuItem value="none">None</MenuItem>
                {Object.values(RecurringTaskPeriod).map((s) => (
                  <MenuItem
                    disabled={comparePeriods(s, period) >= 0}
                    key={s}
                    value={s}
                  >
                    {periodName(s)}
                  </MenuItem>
                ))}
              </Select>
              <FieldError
                actionResult={loaderData}
                fieldName="/breakdown_period"
              />
            </FormControl>
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

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error running the report! Please try again!`
);
