/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserScoreAtDate } from './UserScoreAtDate';
/**
 * A history of user scores over time.
 */
export type UserScoreHistory = {
    daily_scores: Array<UserScoreAtDate>;
    weekly_scores: Array<UserScoreAtDate>;
    monthly_scores: Array<UserScoreAtDate>;
    quarterly_scores: Array<UserScoreAtDate>;
};

