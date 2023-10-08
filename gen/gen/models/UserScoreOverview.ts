/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { UserScore } from './UserScore';

export type UserScoreOverview = {
    daily_score: UserScore;
    weekly_score: UserScore;
    monthly_score: UserScore;
    quarterly_score: UserScore;
    yearly_score: UserScore;
    lifetime_score: UserScore;
    best_quarterly_daily_score: UserScore;
    best_quarterly_weekly_score: UserScore;
    best_quarterly_monthly_score: UserScore;
    best_yearly_daily_score: UserScore;
    best_yearly_weekly_score: UserScore;
    best_yearly_monthly_score: UserScore;
    best_yearly_quarterly_score: UserScore;
    best_lifetime_daily_score: UserScore;
    best_lifetime_weekly_score: UserScore;
    best_lifetime_monthly_score: UserScore;
    best_lifetime_quarterly_score: UserScore;
    best_lifetime_yearly_score: UserScore;
};

