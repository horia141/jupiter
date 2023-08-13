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
import { useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import {
  ApiError,
  NamedEntityTag,
  SearchMatch,
  SearchResult,
} from "jupiter-gen";
import { useContext, useEffect, useState } from "react";
import { z } from "zod";
import { CheckboxAsString, parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { SlimChip } from "~/components/infra/chips";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { ToolCard } from "~/components/infra/tool-card";
import { EntityTagSelect } from "~/components/named-entity-tag-select";
import { TimeDiffTag } from "~/components/time-diff-tag";
import {
  ActionResult,
  isNoErrorSomeData,
  noErrorSomeData,
  validationErrorToUIErrorInfo,
} from "~/logic/action-result";
import { fixSelectOutputToEnum, selectZod } from "~/logic/select";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

export const handle = {
  displayType: DisplayType.LEAF,
};

const QuerySchema = {
  query: z.string().optional(),
  includeArchived: CheckboxAsString,
  filterEntityTags: selectZod(z.nativeEnum(NamedEntityTag)).optional(),
};

interface LoaderResult {
  query: string | undefined;
  includeArchived: boolean;
  filterEntityTags: Array<NamedEntityTag> | undefined;
  result: SearchResult | undefined;
}

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { query, includeArchived, filterEntityTags } = parseQuery(
    request,
    QuerySchema
  );

  console.log(filterEntityTags);

  if (query === undefined) {
    return json(
      noErrorSomeData({
        query: undefined,
        includeArchived: false,
        filterEntityTags: undefined,
        result: undefined,
      })
    );
  }

  try {
    const searchResponse = await getLoggedInApiClient(session).search.search({
      query: { the_query: query },
      limit: { the_limit: 30 },
      include_archived: includeArchived,
      filter_entity_tags:
        fixSelectOutputToEnum<NamedEntityTag>(filterEntityTags),
    });

    return json(
      noErrorSomeData({
        query: query,
        includeArchived: includeArchived,
        filterEntityTags: filterEntityTags,
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

export default function Search() {
  const loaderData = useLoaderDataSafeForAnimation<
    typeof loader
  >() as ActionResult<LoaderResult>;
  const topLevelInfo = useContext(TopLevelInfoContext);
  const transition = useTransition();

  const [searchQuery, setSearchQuery] = useState(
    isNoErrorSomeData(loaderData) ? loaderData.data.query || "" : ""
  );
  const [searchIncludeArchived, setSearchIncludeArchived] = useState(
    isNoErrorSomeData(loaderData)
      ? loaderData.data.includeArchived || false
      : false
  );
  const [searchFilterEntityTags, setSearchFilterEntityTags] = useState(
    isNoErrorSomeData(loaderData) ? loaderData.data.filterEntityTags || [] : []
  );

  useEffect(() => {
    setSearchQuery(
      isNoErrorSomeData(loaderData) ? loaderData.data.query || "" : ""
    );
    setSearchIncludeArchived(
      isNoErrorSomeData(loaderData)
        ? loaderData.data.includeArchived || false
        : false
    );
    setSearchFilterEntityTags(
      isNoErrorSomeData(loaderData)
        ? loaderData.data.filterEntityTags || []
        : []
    );
  }, [loaderData]);

  const inputsEnabled = transition.state === "idle";

  return (
    <ToolCard method="get" returnLocation="?workspace">
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
                  <InputLabel id="filterEntityTags">Filter Entities</InputLabel>
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
        <EntityStack>
          {loaderData.data.result.matches.map((match) => {
            return (
              <EntityCard
                showAsArchived={match.archived}
                key={`${match.entity_tag}:${match.ref_id.the_id}`}
              >
                <Match match={match} />
              </EntityCard>
            );
          })}
        </EntityStack>
      )}
    </ToolCard>
  );
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error performing the search!`
);

interface MatchProps {
  match: SearchMatch;
}

function Match({ match }: MatchProps) {
  const commonSequence = (
    <>
      <MatchSnippet snippet={match.match_snippet} />
      {match.archived && (
        <TimeDiffTag
          labelPrefix="Archived"
          collectionTime={match.archived_time}
        />
      )}
      {!match.archived && (
        <TimeDiffTag
          labelPrefix="Modified"
          collectionTime={match.last_modified_time}
        />
      )}
    </>
  );

  switch (match.entity_tag) {
    case NamedEntityTag.INBOX_TASK:
      return (
        <EntityLink to={`/workspace/inbox-tasks/${match.ref_id.the_id}`}>
          <SlimChip label={"Inbox Task"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.HABIT:
      return (
        <EntityLink to={`/workspace/habits/${match.ref_id.the_id}`}>
          <SlimChip label={"Habit"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.CHORE:
      return (
        <EntityLink to={`/workspace/chores/${match.ref_id.the_id}`}>
          <SlimChip label={"Chore"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.BIG_PLAN:
      return (
        <EntityLink to={`/workspace/big-plans/${match.ref_id.the_id}`}>
          <SlimChip label={"Big Plan"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.VACATION:
      return (
        <EntityLink to={`/workspace/vacations/${match.ref_id.the_id}`}>
          <SlimChip label={"Vacation"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.PROJECT:
      return (
        <EntityLink to={`/workspace/projects/${match.ref_id.the_id}`}>
          <SlimChip label={"Inbox Task"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SMART_LIST:
      return (
        <EntityLink to={`/workspace/smart-lists/${match.ref_id.the_id}`}>
          <SlimChip label={"Smart List"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SMART_LIST_TAG:
      return (
        <EntityLink
          to={`/workspace/smart-lists/${match.parent_ref_id.the_id}/tags/${match.ref_id.the_id}`}
        >
          <SlimChip label={"Smart List Tag"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SMART_LIST_ITEM:
      return (
        <EntityLink
          to={`/workspace/smart-lists/${match.parent_ref_id.the_id}/items/${match.ref_id.the_id}`}
        >
          <SlimChip label={"Smart List Item"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.METRIC:
      return (
        <EntityLink to={`/workspace/metrics/${match.ref_id.the_id}`}>
          <SlimChip label={"Metric"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.METRIC_ENTRY:
      return (
        <EntityLink
          to={`/workspace/metrics/${match.parent_ref_id.the_id}/entries/${match.ref_id.the_id}`}
        >
          <SlimChip label={"Metric Entry"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.PERSON:
      return (
        <EntityLink to={`/workspace/persons/${match.ref_id.the_id}`}>
          <SlimChip label={"Persons"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SLACK_TASK:
      return (
        <EntityLink to={`/workspace/slack-tasks/${match.ref_id.the_id}`}>
          <SlimChip label={"Slack Tasks"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.EMAIL_TASK:
      return (
        <EntityLink to={`/workspace/email-tasks/${match.ref_id.the_id}`}>
          <SlimChip label={"Email Tasks"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
  }
}

interface MatchSnippetProps {
  snippet: string;
}

function MatchSnippet({ snippet }: MatchSnippetProps) {
  const matchSnippetArr: Array<{ text: string; bold: boolean }> = [];

  let currentStr = "";
  let bold = false;
  for (let i = 0; i < snippet.length; i++) {
    if (bold === false && snippet.startsWith("[found]", i)) {
      if (currentStr.length > 0) {
        matchSnippetArr.push({
          text: currentStr,
          bold: false,
        });
      }
      i += 6;
      currentStr = "";
      bold = true;
    } else if (bold === true && snippet.startsWith("[/found]", i)) {
      if (currentStr.length > 0) {
        matchSnippetArr.push({
          text: currentStr,
          bold: true,
        });
      }
      i += 7;
      currentStr = "";
      bold = false;
    } else {
      currentStr += snippet[i];
    }
  }

  if (currentStr.length > 0) {
    matchSnippetArr.push({
      text: currentStr,
      bold: bold,
    });
  }

  return (
    <div>
      {matchSnippetArr.map((item, idx) => {
        if (item.bold) {
          return <strong key={idx}>{item.text}</strong>;
        } else {
          return <span key={idx}>{item.text}</span>;
        }
      })}
    </div>
  );
}
