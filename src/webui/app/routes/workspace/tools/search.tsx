import {
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
} from "@mui/material";
import { ActionArgs, json, LoaderArgs, redirect } from "@remix-run/node";
import { useActionData, useTransition } from "@remix-run/react";
import { StatusCodes } from "http-status-codes";
import {
  ApiError,
  NamedEntityTag,
  SearchMatch,
  SearchResult,
} from "jupiter-gen";
import { z } from "zod";
import { BoolAsString, CheckboxAsString, parseForm, parseQuery } from "zodix";
import { getLoggedInApiClient } from "~/api-clients";
import { EntityCard, EntityLink } from "~/components/infra/entity-card";
import { EntityStack } from "~/components/infra/entity-stack";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { FieldError, GlobalError } from "~/components/infra/errors";
import { SlimChip } from "~/components/infra/slim-chip";
import { ToolCard } from "~/components/infra/tool-card";
import { validationErrorToUIErrorInfo } from "~/logic/action-result";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { DisplayType } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";

export const handle = {
  displayType: DisplayType.LEAF,
};

const QuerySchema = {
  query: z.string().optional(),
  includeArchived: BoolAsString.optional(),
};

const SearchFormSchema = {
  query: z.string(),
  includeArchived: CheckboxAsString,
};

export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const { query, includeArchived } = parseQuery(request, QuerySchema);

  if (query === undefined) {
    return json({
      query: undefined,
      includeArchived: false,
      result: undefined,
    });
  }

  const searchResponse = await getLoggedInApiClient(session).search.search({
    query: query,
    limit: 30,
    include_archived: includeArchived,
  });

  return json({
    query: query,
    includeArchived: includeArchived,
    result: searchResponse,
  });
}

export async function action({ request }: ActionArgs) {
  const form = await parseForm(request, SearchFormSchema);

  try {
    return redirect(
      `/workspace/tools/search?query=${form.query}&includeArchived=${form.includeArchived}`
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
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>() as {
    query: string | undefined;
    includeArchived: boolean;
    result: SearchResult | undefined;
  };
  const actionData = useActionData<typeof action>();
  const transition = useTransition();

  const inputsEnabled = transition.state === "idle";

  return (
    <ToolCard returnLocation="?workspace">
      <Card>
        <GlobalError actionResult={actionData} />
        <CardContent>
          <Stack spacing={2} useFlexGap>
            <FormControl fullWidth>
              <InputLabel id="query">Query</InputLabel>
              <OutlinedInput
                label="Query"
                name="query"
                readOnly={!inputsEnabled}
                defaultValue={loaderData.query || ""}
              />
              <FieldError actionResult={actionData} fieldName="/query" />
            </FormControl>

            <FormControl fullWidth>
              <FormControlLabel
                control={
                  <Switch
                    name="includeArchived"
                    readOnly={!inputsEnabled}
                    defaultChecked={loaderData.includeArchived || false}
                  />
                }
                label="Include Archived"
              />
              <FieldError
                actionResult={actionData}
                fieldName="/include_archived"
              />
            </FormControl>

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

      {loaderData.result && (
        <EntityStack>
          {loaderData.result.matches.map((match) => {
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
  switch (match.entity_tag) {
    case NamedEntityTag.INBOX_TASK:
      return (
        <EntityLink to={`/workspace/inbox-tasks/${match.ref_id.the_id}`}>
          <SlimChip label={"Inbox Task"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
        </EntityLink>
      );
    case NamedEntityTag.HABIT:
      return (
        <EntityLink to={`/workspace/habits/${match.ref_id.the_id}`}>
          <SlimChip label={"Habit"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
        </EntityLink>
      );
    case NamedEntityTag.CHORE:
      return (
        <EntityLink to={`/workspace/chores/${match.ref_id.the_id}`}>
          <SlimChip label={"Chore"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
        </EntityLink>
      );
    case NamedEntityTag.BIG_PLAN:
      return (
        <EntityLink to={`/workspace/big-plans/${match.ref_id.the_id}`}>
          <SlimChip label={"Big Plan"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
        </EntityLink>
      );
    case NamedEntityTag.VACATION:
      return (
        <EntityLink to={`/workspace/vacations/${match.ref_id.the_id}`}>
          <SlimChip label={"Vacation"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
        </EntityLink>
      );
    case NamedEntityTag.PROJECT:
      return (
        <EntityLink to={`/workspace/projects/${match.ref_id.the_id}`}>
          <SlimChip label={"Inbox Task"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
        </EntityLink>
      );
    case NamedEntityTag.SMART_LIST:
      return (
        <EntityLink to={`/workspace/smart-lists/${match.ref_id.the_id}`}>
          <SlimChip label={"Smart List"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
        </EntityLink>
      );
    case NamedEntityTag.SMART_LIST_TAG:
      return (
        <EntityLink to={`/workspace/smart-lists/1/tags/${match.ref_id.the_id}`}>
          <SlimChip label={"Smart List Tag"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
        </EntityLink>
      );
    case NamedEntityTag.SMART_LIST_ITEM:
      return (
        <EntityLink
          to={`/workspace/inbox-tasks/1/items/${match.ref_id.the_id}`}
        >
          <SlimChip label={"Smart List Item"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
        </EntityLink>
      );
    case NamedEntityTag.METRIC:
      return (
        <EntityLink to={`/workspace/metrics/${match.ref_id.the_id}`}>
          <SlimChip label={"Metric"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
        </EntityLink>
      );
    case NamedEntityTag.METRIC_ENTRY:
      return (
        <EntityLink to={`/workspace/metrics/1/entries/${match.ref_id.the_id}`}>
          <SlimChip label={"Metric Entry"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
        </EntityLink>
      );
    case NamedEntityTag.PERSON:
      return (
        <EntityLink to={`/workspace/person/${match.ref_id.the_id}`}>
          <SlimChip label={"Persons"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
        </EntityLink>
      );
    case NamedEntityTag.SLACK_TASK:
      return (
        <EntityLink to={`/workspace/slack-tasks/${match.ref_id.the_id}`}>
          <SlimChip label={"Slack Tasks"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
        </EntityLink>
      );
    case NamedEntityTag.EMAIL_TASK:
      return (
        <EntityLink to={`/workspace/email-tasks/${match.ref_id.the_id}`}>
          <SlimChip label={"Email Tasks"} color={"primary"} />
          <MatchSnippet snippet={match.match_snippet} />
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
