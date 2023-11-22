/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EventSource } from './EventSource';
import type { SyncTarget } from './SyncTarget';

export type GCDoArgs = {
    source: EventSource;
    gc_targets?: Array<SyncTarget>;
};

