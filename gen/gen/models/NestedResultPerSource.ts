/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { InboxTaskSource } from './InboxTaskSource';

/**
 * A particular result broken down by the various sources of inbox tasks.
 */
export type NestedResultPerSource = {
    source: InboxTaskSource;
    count: number;
};

