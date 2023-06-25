/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { WorkableBigPlan } from './WorkableBigPlan';

export type WorkableSummary = {
    created_cnt: number;
    accepted_cnt: number;
    working_cnt: number;
    not_done_cnt: number;
    done_cnt: number;
    not_done_big_plans: Array<WorkableBigPlan>;
    done_big_plans: Array<WorkableBigPlan>;
};

