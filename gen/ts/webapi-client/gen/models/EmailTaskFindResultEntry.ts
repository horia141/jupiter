/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EmailTask } from './EmailTask';
import type { InboxTask } from './InboxTask';

/**
 * A single email task result.
 */
export type EmailTaskFindResultEntry = {
    email_task: EmailTask;
    inbox_task?: (InboxTask | null);
};

