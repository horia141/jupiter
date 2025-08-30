import { PropsWithChildren, useEffect, useState } from "react";
import { DateTime } from "luxon";

import { TopLevelInfo, TopLevelInfoContext } from "~/top-level-context";

const REFRESH_TODAY_MS = 1000; // 1 hour

type TopLevelInfoProviderProps = Omit<TopLevelInfo, "today">;

export function TopLevelInfoProvider(
  props: PropsWithChildren<TopLevelInfoProviderProps>,
) {
  const rightNow = DateTime.local({ zone: props.user.timezone });
  const [today, setToday] = useState(rightNow.toISODate());

  useEffect(() => {
    const timeout = setInterval(() => {
      const rightNow = DateTime.local({ zone: props.user.timezone });
      setToday(rightNow.toISODate());
    }, REFRESH_TODAY_MS);

    return () => {
      clearInterval(timeout);
    };
  }, [props.user.timezone]);

  const topLevelInfo = {
    today,
    userFeatureFlagControls: props.userFeatureFlagControls,
    workspaceFeatureFlagControls: props.workspaceFeatureFlagControls,
    user: props.user,
    userScoreOverview: props.userScoreOverview,
    workspace: props.workspace,
  };

  return (
    <TopLevelInfoContext.Provider value={topLevelInfo}>
      {props.children}
    </TopLevelInfoContext.Provider>
  );
}
