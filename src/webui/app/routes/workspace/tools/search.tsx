import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Button,
  ButtonGroup,
  Card,
  CardActions,
  CardContent,
  FormControl,
  FormControlLabel,
  InputLabel,
  OutlinedInput,
  Stack,
  Switch,
  Typography,
} from "@mui/material";
import { json, LoaderArgs } from "@remix-run/node";
import { ShouldRevalidateFunction, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import { ApiError, NamedEntityTag } from "jupiter-gen";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { CheckboxAsString, parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntitySummaryLink } from "~/components/entity-summary-link";
import { EntityCard } from "~/components/infra/entity-card";
import { EntityStack2 } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolPanel } from "~/components/infra/layout/tool-panel";
import { EntityTagSelect } from "~/components/named-entity-tag-select";
import {
  isNoErrorSomeData,
  noErrorSomeData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { fixSelectOutputToEnum, selectZod } from "~/logic/select";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.TOOL,
};

const QuerySchema = {
  query: z.string().optional(),
  limit: z.string().optional(),
  includeArchived: CheckboxAsString,
  filterEntityTags: selectZod(z.nativeEnum(NamedEntityTag)).optional(),
  filterCreatedTimeAfter: z.string().optional(),
  filterCreatedTimeBefore: z.string().optional(),
  filterLastModifiedTimeAfter: z.string().optional(),
  filterLastModifiedTimeBefore: z.string().optional(),
  filterArchivedTimeAfter: z.string().optional(),
  filterArchivedTimeBefore: z.string().optional(),
};

const DEFAULT_LIMIT = 30;

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const query = parseQuery(request, QuerySchema);

  try {
    let searchResponse = undefined;
    if (query.query !== undefined) {
      searchResponse = await getLoggedInApiClient(session).search.search({
        query: query.query,
        limit: query.limit ? parseInt(query.limit) : DEFAULT_LIMIT,
        include_archived: query.includeArchived,
        filter_entity_tags: fixSelectOutputToEnum<NamedEntityTag>(
          query.filterEntityTags
        ),
        filter_created_time_after: query.filterCreatedTimeAfter,
        filter_created_time_before: query.filterCreatedTimeBefore,
        filter_last_modified_time_after: query.filterLastModifiedTimeAfter,
        filter_last_modified_time_before: query.filterLastModifiedTimeBefore,
        filter_archived_time_after: query.filterArchivedTimeAfter,
        filter_archived_time_before: query.filterArchivedTimeBefore,
      });
    }

    return json(
      noErrorSomeData({
        query: query.query,
        limit: query.limit,
        includeArchived: query.includeArchived,
        filterEntityTags: fixSelectOutputToEnum<NamedEntityTag>(
          query.filterEntityTags
        ),
        filterCreatedTimeAfter: query.filterCreatedTimeAfter,
        filterCreatedTimeBefore: query.filterCreatedTimeBefore,
        filterLastModifiedTimeAfter: query.filterLastModifiedTimeAfter,
        filterLastModifiedTimeBefore: query.filterLastModifiedTimeBefore,
        filterArchivedTimeAfter: query.filterArchivedTimeAfter,
        filterArchivedTimeBefore: query.filterArchivedTimeBefore,
        result: searchResponse,
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

export default function Search() {
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const topLevelInfo = useContext(TopLevelInfoContext);
  const transition = useTransition();

  const isBigScreen = useBigScreen();

  const [searchQuery, setSearchQuery] = useState(
    isNoErrorSomeData(loaderData) ? loaderData.data.query : ""
  );
  const [searchLimit, setSearchLimit] = useState(
    isNoErrorSomeData(loaderData) ? loaderData.data.limit : undefined
  );
  const [searchIncludeArchived, setSearchIncludeArchived] = useState(
    isNoErrorSomeData(loaderData) ? loaderData.data.includeArchived : false
  );
  const [searchFilterEntityTags, setSearchFilterEntityTags] = useState(
    isNoErrorSomeData(loaderData) ? loaderData.data.filterEntityTags || [] : []
  );
  const [searchFilterCreatedTimeAfter, setSearchFilterCreatedTimeAfter] =
    useState(
      isNoErrorSomeData(loaderData)
        ? loaderData.data.filterCreatedTimeAfter
        : undefined
    );
  const [searchFilterCreatedTimeBefore, setSearchFilterCreatedTimeBefore] =
    useState(
      isNoErrorSomeData(loaderData)
        ? loaderData.data.filterCreatedTimeBefore
        : undefined
    );
  const [
    searchFilterLastModifiedTimeAfter,
    setSearchFilterLastModifiedTimeAfter,
  ] = useState(
    isNoErrorSomeData(loaderData)
      ? loaderData.data.filterLastModifiedTimeAfter
      : undefined
  );
  const [
    searchFilterLastModifiedTimeBefore,
    setSearchFilterLastModifiedTimeBefore,
  ] = useState(
    isNoErrorSomeData(loaderData)
      ? loaderData.data.filterLastModifiedTimeBefore
      : undefined
  );
  const [searchFilterArchivedTimeAfter, setSearchFilterArchivedTimeAfter] =
    useState(
      isNoErrorSomeData(loaderData)
        ? loaderData.data.filterArchivedTimeAfter
        : undefined
    );
  const [searchFilterArchivedTimeBefore, setSearchFilterArchivedTimeBefore] =
    useState(
      isNoErrorSomeData(loaderData)
        ? loaderData.data.filterArchivedTimeBefore
        : undefined
    );

  useEffect(() => {
    setSearchQuery(isNoErrorSomeData(loaderData) ? loaderData.data.query : "");
    setSearchLimit(
      isNoErrorSomeData(loaderData) ? loaderData.data.limit : undefined
    );
    setSearchIncludeArchived(
      isNoErrorSomeData(loaderData) ? loaderData.data.includeArchived : false
    );
    setSearchFilterEntityTags(
      isNoErrorSomeData(loaderData)
        ? loaderData.data.filterEntityTags || []
        : []
    );
    setSearchFilterCreatedTimeAfter(
      isNoErrorSomeData(loaderData)
        ? loaderData.data.filterCreatedTimeAfter
        : undefined
    );
    setSearchFilterCreatedTimeBefore(
      isNoErrorSomeData(loaderData)
        ? loaderData.data.filterCreatedTimeBefore
        : undefined
    );
    setSearchFilterLastModifiedTimeAfter(
      isNoErrorSomeData(loaderData)
        ? loaderData.data.filterLastModifiedTimeAfter
        : undefined
    );
    setSearchFilterLastModifiedTimeBefore(
      isNoErrorSomeData(loaderData)
        ? loaderData.data.filterLastModifiedTimeBefore
        : undefined
    );
    setSearchFilterArchivedTimeAfter(
      isNoErrorSomeData(loaderData)
        ? loaderData.data.filterArchivedTimeAfter
        : undefined
    );
    setSearchFilterArchivedTimeBefore(
      isNoErrorSomeData(loaderData)
        ? loaderData.data.filterArchivedTimeBefore
        : undefined
    );
  }, [loaderData]);

  const inputsEnabled = transition.state === "idle";

  return (
    <ToolPanel method="get">
      <Card>
        <GlobalError actionResult={loaderData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="query">Query</InputLabel>
              <OutlinedInput
                label="Query"
                name="query"
                readOnly={!inputsEnabled}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <FieldError actionResult={loaderData} fieldName="/query" />
            </FormControl>

            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>Advanced</Typography>
              </AccordionSummary>

              <AccordionDetails>
                <Stack useFlexGap spacing={2}>
                  <Stack
                    useFlexGap
                    sx={{ alignItems: "center" }}
                    direction={isBigScreen ? "row" : "column"}
                    spacing={2}
                  >
                    <FormControl fullWidth>
                      <InputLabel id="limit">Limit</InputLabel>
                      <OutlinedInput
                        label="Limit"
                        name="limit"
                        type="number"
                        readOnly={!inputsEnabled}
                        value={searchLimit}
                        onChange={(e) => setSearchLimit(e.target.value)}
                      />
                      <FieldError
                        actionResult={loaderData}
                        fieldName="/limit"
                      />
                    </FormControl>

                    <FormControl fullWidth>
                      <FormControlLabel
                        control={
                          <Switch
                            name="includeArchived"
                            readOnly={!inputsEnabled}
                            checked={searchIncludeArchived}
                            onChange={(e) =>
                              setSearchIncludeArchived(e.target.checked)
                            }
                          />
                        }
                        label="Include Archived"
                      />
                      <FieldError
                        actionResult={loaderData}
                        fieldName="/include_archived"
                      />
                    </FormControl>

                    <FormControl fullWidth>
                      <InputLabel id="filterEntityTags">
                        Filter Entities
                      </InputLabel>
                      <EntityTagSelect
                        topLevelInfo={topLevelInfo}
                        labelId="filterEntityTags"
                        label="Filter Entities"
                        name="filterEntityTags"
                        readOnly={!inputsEnabled}
                        value={searchFilterEntityTags}
                        onChange={(e) => setSearchFilterEntityTags(e)}
                      />
                      <FieldError
                        actionResult={loaderData}
                        fieldName="/filter_entity_tags"
                      />
                    </FormControl>
                  </Stack>

                  <Stack
                    spacing={2}
                    useFlexGap
                    direction={isBigScreen ? "row" : "column"}
                  >
                    <Stack spacing={2} useFlexGap sx={{ flexGrow: 1 }}>
                      <FormControl fullWidth>
                        <InputLabel id="filterCreatedTimeAfter">
                          Created After
                        </InputLabel>
                        <OutlinedInput
                          type="date"
                          label="Created After"
                          value={searchFilterCreatedTimeAfter}
                          onChange={(e) =>
                            setSearchFilterCreatedTimeAfter(e.target.value)
                          }
                          name="filterCreatedTimeAfter"
                          readOnly={!inputsEnabled}
                        />

                        <FieldError
                          actionResult={loaderData}
                          fieldName="/filter_created_time_after"
                        />
                      </FormControl>

                      <FormControl fullWidth>
                        <InputLabel id="filterCreatedTimeBefore">
                          Created Before
                        </InputLabel>
                        <OutlinedInput
                          type="date"
                          label="Created Before"
                          value={searchFilterCreatedTimeBefore}
                          onChange={(e) =>
                            setSearchFilterCreatedTimeBefore(e.target.value)
                          }
                          name="filterCreatedTimeBefore"
                          readOnly={!inputsEnabled}
                        />

                        <FieldError
                          actionResult={loaderData}
                          fieldName="/filter_created_time_before"
                        />
                      </FormControl>
                    </Stack>

                    <Stack spacing={2} useFlexGap sx={{ flexGrow: 1 }}>
                      <FormControl fullWidth>
                        <InputLabel id="filterLastModifiedTimeAfter">
                          Last Modified After
                        </InputLabel>
                        <OutlinedInput
                          type="date"
                          label="Last Modified After"
                          value={searchFilterLastModifiedTimeAfter}
                          onChange={(e) =>
                            setSearchFilterLastModifiedTimeAfter(e.target.value)
                          }
                          name="filterLastModifiedTimeAfter"
                          readOnly={!inputsEnabled}
                        />

                        <FieldError
                          actionResult={loaderData}
                          fieldName="/filter_last_modified_time_after"
                        />
                      </FormControl>

                      <FormControl fullWidth>
                        <InputLabel id="filterLastModifiedTimeBefore">
                          Last Modified Before
                        </InputLabel>
                        <OutlinedInput
                          type="date"
                          label="Last Modified Before"
                          value={searchFilterLastModifiedTimeBefore}
                          onChange={(e) =>
                            setSearchFilterLastModifiedTimeBefore(
                              e.target.value
                            )
                          }
                          name="filterLastModifiedTimeBefore"
                          readOnly={!inputsEnabled}
                        />

                        <FieldError
                          actionResult={loaderData}
                          fieldName="/filter_last_modified_time_before"
                        />
                      </FormControl>
                    </Stack>

                    <Stack spacing={2} useFlexGap sx={{ flexGrow: 1 }}>
                      <FormControl fullWidth>
                        <InputLabel id="filterArchivedTimeAfter">
                          Archived After
                        </InputLabel>
                        <OutlinedInput
                          type="date"
                          label="Archived After"
                          value={searchFilterArchivedTimeAfter}
                          onChange={(e) =>
                            setSearchFilterArchivedTimeAfter(e.target.value)
                          }
                          name="filterArchivedTimeAfter"
                          readOnly={!inputsEnabled}
                        />

                        <FieldError
                          actionResult={loaderData}
                          fieldName="/filter_archived_time_after"
                        />
                      </FormControl>

                      <FormControl fullWidth>
                        <InputLabel id="filterArchivedTimeBefore">
                          Archived Before
                        </InputLabel>
                        <OutlinedInput
                          type="date"
                          label="Archived Before"
                          value={searchFilterArchivedTimeBefore}
                          onChange={(e) =>
                            setSearchFilterArchivedTimeBefore(e.target.value)
                          }
                          name="filterArchivedTimeBefore"
                          readOnly={!inputsEnabled}
                        />

                        <FieldError
                          actionResult={loaderData}
                          fieldName="/filter_archived_time_before"
                        />
                      </FormControl>
                    </Stack>
                  </Stack>
                </Stack>
              </AccordionDetails>
            </Accordion>

            <CardActions>
              <ButtonGroup>
                <Button
                  variant="contained"
                  disabled={!inputsEnabled}
                  type="submit"
                >
                  Search
                </Button>
              </ButtonGroup>
            </CardActions>
          </Stack>
        </CardContent>
      </Card>

      {isNoErrorSomeData(loaderData) && loaderData.data.result && (
        <EntityStack2>
          <Typography>
            Showing {loaderData.data.result.matches.length} results out of{" "}
            {loaderData.data.limit ? loaderData.data.limit : DEFAULT_LIMIT}{" "}
            asked
          </Typography>
          {loaderData.data.result.matches.map((match) => {
            return (
              <EntityCard
                showAsArchived={match.summary.archived}
                key={`${match.summary.entity_tag}:${match.summary.ref_id}`}
              >
                <EntitySummaryLink summary={match.summary} />
              </EntityCard>
            );
          })}
        </EntityStack2>
      )}
    </ToolPanel>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error performing the search!`
);
