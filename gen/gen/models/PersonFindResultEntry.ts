/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { InboxTask } from './InboxTask';
import type { Note } from './Note';
import type { Person } from './Person';

/**
 * A single person result.
 */
export type PersonFindResultEntry = {
    person: Person;
    catch_up_inbox_tasks?: Array<InboxTask>;
    birthday_inbox_tasks?: Array<InboxTask>;
    note?: Note;
};

