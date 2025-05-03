import type { EntitySummary } from "@jupiter/webapi-client";
import { NamedEntityTag } from "@jupiter/webapi-client";
import type { DateTime } from "luxon";

import { SlimChip } from "~/components/infra/chips";
import { EntityFakeLink, EntityLink } from "~/components/infra/entity-card";
import { TimeDiffTag } from "~/components/domain/core/time-diff-tag";

interface EntitySummaryLinkProps {
  today: DateTime;
  summary: EntitySummary;
  removed?: boolean;
}

export function EntitySummaryLink({
  today,
  summary,
  removed,
}: EntitySummaryLinkProps) {
  const commonSequence = (
    <>
      <MatchSnippet snippet={summary.snippet} />
      {summary.archived && summary.archived_time && (
        <TimeDiffTag
          today={today}
          labelPrefix="Archived"
          collectionTime={summary.archived_time}
        />
      )}
      {!summary.archived && (
        <TimeDiffTag
          today={today}
          labelPrefix="Modified"
          collectionTime={summary.last_modified_time}
        />
      )}
    </>
  );

  if (removed) {
    return (
      <EntityFakeLink>
        <SlimChip label={"Removed Entity"} color={"primary"} />
        {commonSequence}
      </EntityFakeLink>
    );
  }

  switch (summary.entity_tag) {
    case NamedEntityTag.SCORE_LOG_ENTRY:
      return (
        <EntityLink to={"/nowhere"} block>
          <SlimChip label={"Score Log Entry"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.INBOX_TASK:
      return (
        <EntityLink to={`/app/workspace/inbox-tasks/${summary.ref_id}`}>
          <SlimChip label={"Inbox Task"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.WORKING_MEM:
      return (
        <EntityLink to={`/app/workspace/working-mem/archive/${summary.ref_id}`}>
          <SlimChip label={"Working Mem"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.TIME_PLAN:
      return (
        <EntityLink to={`/app/workspace/time-plans/${summary.ref_id}`}>
          <SlimChip label={"Time Plan"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.TIME_PLAN_ACTIVITY:
      return (
        <EntityLink
          to={`/app/workspace/time-plans/${summary.parent_ref_id}/activities/${summary.ref_id}`}
        >
          <SlimChip label={"Time Plan Acticity"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SCHEDULE_STREAM:
      return (
        <EntityLink
          to={`/app/workspace/calendar/schedule/stream/${summary.ref_id}`}
        >
          <SlimChip label={"Schedule Stream"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SCHEDULE_EVENT_IN_DAY:
      return (
        <EntityLink
          to={`/app/workspace/calendar/schedule/event-in-day/${summary.ref_id}`}
        >
          <SlimChip label={"Schedule Event In Day"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SCHEDULE_EVENT_FULL_DAYS:
      return (
        <EntityLink
          to={`/app/workspace/calendar/schedule/event-full-days/${summary.ref_id}`}
        >
          <SlimChip label={"Schedule Event Full Days"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SCHEDULE_EXTERNAL_SYNC_LOG:
      return <></>; // This isn't really a supported entity
    case NamedEntityTag.HABIT:
      return (
        <EntityLink to={`/app/workspace/habits/${summary.ref_id}`}>
          <SlimChip label={"Habit"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.CHORE:
      return (
        <EntityLink to={`/app/workspace/chores/${summary.ref_id}`}>
          <SlimChip label={"Chore"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.BIG_PLAN:
      return (
        <EntityLink to={`/app/workspace/big-plans/${summary.ref_id}`}>
          <SlimChip label={"Big Plan"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.JOURNAL:
      return (
        <EntityLink to={`/app/workspace/journals/${summary.ref_id}`}>
          <SlimChip label={"Journal"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.DOC:
      return (
        <EntityLink to={`/app/workspace/docs/${summary.ref_id}`}>
          <SlimChip label={"Doc"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.VACATION:
      return (
        <EntityLink to={`/app/workspace/vacations/${summary.ref_id}`}>
          <SlimChip label={"Vacation"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.PROJECT:
      return (
        <EntityLink to={`/app/workspace/projects/${summary.ref_id}`}>
          <SlimChip label={"Inbox Task"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SMART_LIST:
      return (
        <EntityLink to={`/app/workspace/smart-lists/${summary.ref_id}/items`}>
          <SlimChip label={"Smart List"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SMART_LIST_TAG:
      return (
        <EntityLink
          to={`/app/workspace/smart-lists/${summary.parent_ref_id}/tags/${summary.ref_id}`}
        >
          <SlimChip label={"Smart List Tag"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SMART_LIST_ITEM:
      return (
        <EntityLink
          to={`/app/workspace/smart-lists/${summary.parent_ref_id}/items/${summary.ref_id}`}
        >
          <SlimChip label={"Smart List Item"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.METRIC:
      return (
        <EntityLink to={`/app/workspace/metrics/${summary.ref_id}/entries`}>
          <SlimChip label={"Metric"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.METRIC_ENTRY:
      return (
        <EntityLink
          to={`/app/workspace/metrics/${summary.parent_ref_id}/entries/${summary.ref_id}`}
        >
          <SlimChip label={"Metric Entry"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.PERSON:
      return (
        <EntityLink to={`/app/workspace/persons/${summary.ref_id}`}>
          <SlimChip label={"Persons"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SLACK_TASK:
      return (
        <EntityLink to={`/app/workspace/slack-tasks/${summary.ref_id}`}>
          <SlimChip label={"Slack Tasks"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.EMAIL_TASK:
      return (
        <EntityLink to={`/app/workspace/email-tasks/${summary.ref_id}`}>
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
