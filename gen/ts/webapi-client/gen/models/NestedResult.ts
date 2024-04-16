/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { NestedResultPerSource } from './NestedResultPerSource';

/**
 * A result broken down by the various sources of inbox tasks.
 */
export type NestedResult = {
    total_cnt: number;
    per_source_cnt: Array<NestedResultPerSource>;
};

