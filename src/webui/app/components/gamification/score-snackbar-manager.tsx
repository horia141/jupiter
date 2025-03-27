import Cookies from "js-cookie";
import { useSnackbar } from "notistack";
import { useEffect, useState } from "react";
import type { ScoreAction } from "~/logic/domain/gamification/scores";
import { SCORE_ACTION_COOKIE_SCHEMA } from "~/logic/domain/gamification/scores";
import { SCORE_ACTION_COOKIE_NAME } from "~/names";
import { useBigScreen } from "~/rendering/use-big-screen";

function formatScoreUpdate(result: ScoreAction, isBigScreen: boolean): string {
  let resultStr = "";

  const pointsStr =
    Math.abs(result.latest_task_score) === 1 ? "point" : "points";

  if (result.latest_task_score > 0) {
    resultStr += `⭐ Great! You scored ${result.latest_task_score} ${pointsStr}!`;
  } else {
    resultStr += `😿 Snap! You lost ${Math.abs(
      result.latest_task_score,
    )} ${pointsStr}!`;
  }

  if (result.has_lucky_puppy_bonus) {
    resultStr += " You got a 🐶lucky puppy🐶 bonus! ";
  }

  if (isBigScreen) {
    resultStr += ` Which brings your total for today to ${result.daily_total_score} and for this week to ${result.weekly_total_score}.`;
  }

  return resultStr;
}

export function useScoreActionSingleton() {
  const [scoreAction, setScoreAction] = useState<ScoreAction | undefined>(
    undefined,
  );

  useEffect(() => {
    const interval = setInterval(() => {
      const scoreActionStr = Cookies.get(SCORE_ACTION_COOKIE_NAME);
      if (scoreActionStr === undefined) {
        return;
      }
      const scoreAction = SCORE_ACTION_COOKIE_SCHEMA.parse(
        JSON.parse(atob(scoreActionStr)),
      );
      setScoreAction(scoreAction);
      Cookies.remove(SCORE_ACTION_COOKIE_NAME);
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return scoreAction;
}

interface ScoreSnackbarManagerProps {
  scoreAction: ScoreAction | undefined;
}

export function ScoreSnackbarManager({
  scoreAction,
}: ScoreSnackbarManagerProps) {
  const { enqueueSnackbar } = useSnackbar();
  const isBigScreen = useBigScreen();

  useEffect(() => {
    if (scoreAction !== undefined) {
      enqueueSnackbar(formatScoreUpdate(scoreAction, isBigScreen), {
        key: "gamification",
        autoHideDuration: 3000,
        hideIconVariant: true,
        variant: scoreAction.latest_task_score > 0 ? "success" : "warning",
      });
    }
  }, [enqueueSnackbar, isBigScreen, scoreAction]);

  return null;
}
