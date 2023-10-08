/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { UserScoreAtDate } from './UserScoreAtDate';

export type UserScoreHistory = {
    daily_scores: Array<UserScoreAtDate>;
    weekly_scores: Array<UserScoreAtDate>;
    monthly_scores: Array<UserScoreAtDate>;
    quarterly_scores: Array<UserScoreAtDate>;
};

