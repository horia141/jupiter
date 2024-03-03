/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { User } from './User';
import type { UserScoreHistory } from './UserScoreHistory';
import type { UserScoreOverview } from './UserScoreOverview';

/**
 * User find result.
 */
export type UserLoadResult = {
    user: User;
    user_score_overview?: UserScoreOverview;
    user_score_history?: UserScoreHistory;
};

