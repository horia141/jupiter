/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { TimeEventNamespace } from './TimeEventNamespace';

/**
 * Just a slice of the stats.
 */
export type TimeEventInDayBlockStatsPerGroup = {
    date: ADate;
    namespace: TimeEventNamespace;
    cnt: number;
};

