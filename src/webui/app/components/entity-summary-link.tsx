import { EntitySummary, NamedEntityTag } from "jupiter-gen";
import { SlimChip } from "./infra/chips";
import { EntityFakeLink, EntityLink } from "./infra/entity-card";
import { TimeDiffTag } from "./time-diff-tag";

interface EntitySummaryLinkProps {
  summary: EntitySummary;
  removed?: boolean;
}

export function EntitySummaryLink({
  summary,
  removed,
}: EntitySummaryLinkProps) {
  const commonSequence = (
    <>
      <MatchSnippet snippet={summary.snippet} />
      {summary.archived && summary.archived_time && (
        <TimeDiffTag
          labelPrefix="Archived"
          collectionTime={summary.archived_time}
        />
      )}
      {!summary.archived && (
        <TimeDiffTag
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
    case NamedEntityTag.INBOX_TASK:
      return (
        <EntityLink to={`/workspace/inbox-tasks/${summary.ref_id}`}>
          <SlimChip label={"Inbox Task"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.HABIT:
      return (
        <EntityLink to={`/workspace/habits/${summary.ref_id}`}>
          <SlimChip label={"Habit"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.CHORE:
      return (
        <EntityLink to={`/workspace/chores/${summary.ref_id}`}>
          <SlimChip label={"Chore"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.BIG_PLAN:
      return (
        <EntityLink to={`/workspace/big-plans/${summary.ref_id}`}>
          <SlimChip label={"Big Plan"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.JOURNAL:
      return (
        <EntityLink to={`/workspace/journals/${summary.ref_id}`}>
          <SlimChip label={"Journal"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.DOC:
      return (
        <EntityLink to={`/workspace/docs/${summary.ref_id}`}>
          <SlimChip label={"Doc"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.VACATION:
      return (
        <EntityLink to={`/workspace/vacations/${summary.ref_id}`}>
          <SlimChip label={"Vacation"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.PROJECT:
      return (
        <EntityLink to={`/workspace/projects/${summary.ref_id}`}>
          <SlimChip label={"Inbox Task"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SMART_LIST:
      return (
        <EntityLink to={`/workspace/smart-lists/${summary.ref_id}/items`}>
          <SlimChip label={"Smart List"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SMART_LIST_TAG:
      return (
        <EntityLink
          to={`/workspace/smart-lists/${summary.parent_ref_id}/tags/${summary.ref_id}`}
        >
          <SlimChip label={"Smart List Tag"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SMART_LIST_ITEM:
      return (
        <EntityLink
          to={`/workspace/smart-lists/${summary.parent_ref_id}/items/${summary.ref_id}`}
        >
          <SlimChip label={"Smart List Item"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.METRIC:
      return (
        <EntityLink to={`/workspace/metrics/${summary.ref_id}/entries`}>
          <SlimChip label={"Metric"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.METRIC_ENTRY:
      return (
        <EntityLink
          to={`/workspace/metrics/${summary.parent_ref_id}/entries/${summary.ref_id}`}
        >
          <SlimChip label={"Metric Entry"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.PERSON:
      return (
        <EntityLink to={`/workspace/persons/${summary.ref_id}`}>
          <SlimChip label={"Persons"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.SLACK_TASK:
      return (
        <EntityLink to={`/workspace/slack-tasks/${summary.ref_id}`}>
          <SlimChip label={"Slack Tasks"} color={"primary"} />
          {commonSequence}
        </EntityLink>
      );
    case NamedEntityTag.EMAIL_TASK:
      return (
        <EntityLink to={`/workspace/email-tasks/${summary.ref_id}`}>
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
