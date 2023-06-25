/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ADate } from './ADate';
import type { EntityId } from './EntityId';

export type MetricEntryUpdateArgs = {
    ref_id: EntityId;
    collection_time: {
        should_change: boolean;
        value?: ADate;
    };
    value: {
        should_change: boolean;
        value?: number;
    };
    notes: {
        should_change: boolean;
        value?: string;
    };
};

