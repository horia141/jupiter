/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { NestedResult } from './NestedResult';

export type InboxTasksSummary = {
    created: NestedResult;
    accepted: NestedResult;
    working: NestedResult;
    not_done: NestedResult;
    done: NestedResult;
};

