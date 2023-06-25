/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { NestedResultPerSource } from './NestedResultPerSource';

export type NestedResult = {
    total_cnt: number;
    per_source_cnt: Array<NestedResultPerSource>;
};

