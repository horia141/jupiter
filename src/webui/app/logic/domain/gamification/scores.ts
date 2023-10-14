import { z } from "zod";

export interface ScoreAction {
    latest_task_score: number;
    daily_total_score: number;
    weekly_total_score: number;
}

export const SCORE_ACTION_COOKIE_SCHEMA = z.object({
    latest_task_score: z.number(),
    daily_total_score: z.number(),
    weekly_total_score: z.number(),
  });
  