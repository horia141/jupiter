/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EventSource } from './EventSource';
import type { Timestamp } from './Timestamp';

export type Event = {
    source: EventSource;
    entity_version: number;
    timestamp: Timestamp;
    frame_args: any;
};
