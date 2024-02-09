/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventKind } from './EventKind';
import type { EventSource } from './EventSource';
import type { Timestamp } from './Timestamp';
export type Event = {
    source: EventSource;
    entity_version: number;
    timestamp: Timestamp;
    frame_args: Record<string, any>;
    kind: EventKind;
    name: string;
};

