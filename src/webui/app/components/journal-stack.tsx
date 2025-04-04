import type { Journal, ReportPeriodResult } from "@jupiter/webapi-client";
import {
  RecurringTaskPeriod,
  UserFeature,
  WorkspaceFeature,
} from "@jupiter/webapi-client";

import { isUserFeatureAvailable } from "~/logic/domain/user";
import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import type { TopLevelInfo } from "~/top-level-context";

import { EntityNameComponent } from "./entity-name";
import { EntityCard, EntityLink } from "./infra/entity-card";
import { EntityStack } from "./infra/entity-stack";
import { JournalSourceTag } from "./journal-source-tag";
import { PeriodTag } from "./period-tag";

interface JournalStackProps {
  topLevelInfo: TopLevelInfo;
  journals: Array<Journal>;
  allowSwipe?: boolean;
  allowMarkNotDone?: boolean;
  onMarkNotDone?: (journal: Journal) => void;
}

export function JournalStack(props: JournalStackProps) {
  return (
    <EntityStack>
      {props.journals.map((journal) => (
        <EntityCard
          key={`journal-${journal.ref_id}`}
          entityId={`journal-${journal.ref_id}`}
          allowSwipe={props.allowSwipe}
          allowMarkNotDone={props.allowMarkNotDone}
          onMarkNotDone={() =>
            props.onMarkNotDone && props.onMarkNotDone(journal)
          }
        >
          <EntityLink to={`/app/workspace/journals/${journal.ref_id}`}>
            <EntityNameComponent name={journal.name} />
            <JournalSourceTag source={journal.source} />
            <PeriodTag period={journal.period} />
            {isUserFeatureAvailable(
              props.topLevelInfo.user,
              UserFeature.GAMIFICATION,
            ) && (
              <GamificationTag
                period={journal.period}
                report={journal.report}
              />
            )}
            {journal.report.global_inbox_tasks_summary.done.total_cnt} tasks
            done
            {isWorkspaceFeatureAvailable(
              props.topLevelInfo.workspace,
              WorkspaceFeature.BIG_PLANS,
            ) && (
              <>
                {" "}
                and {journal.report.global_big_plans_summary.done_cnt} big plans
                done
              </>
            )}
          </EntityLink>
        </EntityCard>
      ))}
    </EntityStack>
  );
}

interface GamificationTagProps {
  period: RecurringTaskPeriod;
  report: ReportPeriodResult;
}

function GamificationTag({ period, report }: GamificationTagProps) {
  if (!report.user_score_overview) {
    return null;
  }

  switch (period) {
    case RecurringTaskPeriod.DAILY:
      return (
        <>{report.user_score_overview.daily_score.total_score} points from </>
      );
    case RecurringTaskPeriod.WEEKLY:
      return (
        <>{report.user_score_overview.weekly_score.total_score} points from </>
      );
    case RecurringTaskPeriod.MONTHLY:
      return (
        <>{report.user_score_overview.monthly_score.total_score} points from </>
      );
    case RecurringTaskPeriod.QUARTERLY:
      return (
        <>
          {report.user_score_overview.quarterly_score.total_score} points
          from{" "}
        </>
      );
    case RecurringTaskPeriod.YEARLY:
      return (
        <>{report.user_score_overview.yearly_score.total_score} points from </>
      );
  }
}
