import { createCookie } from "@remix-run/node";
import type { RecordScoreResult } from "jupiter-gen";
import { GLOBAL_PROPERTIES } from "~/global-properties-server";

// TODO(horia141): secrets!
const scoreActionCookie = createCookie(
  GLOBAL_PROPERTIES.scoreActionCookieName,
  {
    maxAge: 60 * 60, // 1 hour
    path: "/",
    sameSite: "strict",
  }
);

export async function saveScoreAction(result: RecordScoreResult) {
  return await scoreActionCookie.serialize({
    latest_task_score: result.latest_task_score,
    has_lucky_puppy_bonus: result.has_lucky_puppy_bonus,
    daily_total_score: result.score_overview.daily_score.total_score,
    weekly_total_score: result.score_overview.weekly_score.total_score,
  });
}
