/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Note } from './Note';
import type { ScheduleStream } from './ScheduleStream';

/**
 * A single entry in the load all schedule streams response.
 */
export type ScheduleStreamFindResultEntry = {
    schedule_stream: ScheduleStream;
    note?: (Note | null);
};

