/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserScoreOverview } from './UserScoreOverview';
/**
 * The result of the score recording.
 */
export type RecordScoreResult = {
    latest_task_score: number;
    has_lucky_puppy_bonus?: (boolean | null);
    score_overview: UserScoreOverview;
};

