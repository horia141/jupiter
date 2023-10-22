import { z } from "zod";

export interface ScoreAction {
  latest_task_score: number;
  has_lucky_puppy_bonus: boolean | null;
  daily_total_score: number;
  weekly_total_score: number;
}

export const SCORE_ACTION_COOKIE_SCHEMA = z.object({
  latest_task_score: z.number(),
  has_lucky_puppy_bonus: z.boolean().nullable(),
  daily_total_score: z.number(),
  weekly_total_score: z.number(),
});
