import Cookies from "js-cookie";
import { RecordScoreResult } from "jupiter-gen";
import { useSnackbar } from "notistack";
import { useContext, useEffect, useState } from "react";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { useBigScreen } from "~/rendering/use-big-screen";

function formatScoreUpdate(
  result: RecordScoreResult,
  isBigScreen: boolean
): string {
  let resultStr = "";

  const pointsStr =
    Math.abs(result.latest_task_score) === 1 ? "point" : "points";

  if (result.latest_task_score > 0) {
    resultStr += `⭐ Great! You scored ${result.latest_task_score} ${pointsStr}!`;
  } else {
    resultStr += `😿 Snap! You lost ${Math.abs(
      result.latest_task_score
    )} ${pointsStr}!`;
  }

  if (isBigScreen) {
    resultStr += ` Which brings your total for today to ${result.score_overview.daily_score.total_score} and for this week to ${result.score_overview.weekly_score.total_score}.`;
  }

  return resultStr;
}

export function useScoreActionSingleton() {
  const [scoreAction, setScoreAction] = useState<RecordScoreResult | undefined>(
    undefined
  );

  const globalProperties = useContext(GlobalPropertiesContext);

  useEffect(() => {
    const interval = setInterval(() => {
      const scoreActionStr = Cookies.get(
        globalProperties.scoreActionCookieName
      );
      if (scoreActionStr === undefined) {
        return;
      }
      const scoreAction = JSON.parse(atob(scoreActionStr))
        .result as RecordScoreResult;
      setScoreAction(scoreAction);
      Cookies.remove(globalProperties.scoreActionCookieName);
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return scoreAction;
}

interface ScoreSnackbarManagerProps {
  scoreAction: RecordScoreResult | undefined;
}

export function ScoreSnackbarManager({
  scoreAction,
}: ScoreSnackbarManagerProps) {
  const { enqueueSnackbar } = useSnackbar();
  const isBigScreen = useBigScreen();

  useEffect(() => {
    if (scoreAction !== undefined) {
      enqueueSnackbar(formatScoreUpdate(scoreAction, isBigScreen), {
        autoHideDuration: 3000,
        hideIconVariant: true,
        variant: scoreAction.latest_task_score > 0 ? "success" : "warning",
      });
    }
  }, [scoreAction]);

  return null;
}
