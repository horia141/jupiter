/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { InboxTask } from './InboxTask';
import type { Note } from './Note';
import type { Person } from './Person';
import type { TimeEventFullDaysBlock } from './TimeEventFullDaysBlock';

/**
 * PersonLoadResult.
 */
export type PersonLoadResult = {
    person: Person;
    birthday_time_event_blocks: Array<TimeEventFullDaysBlock>;
    catch_up_inbox_tasks: Array<InboxTask>;
    birthday_inbox_tasks: Array<InboxTask>;
    note?: (Note | null);
};

