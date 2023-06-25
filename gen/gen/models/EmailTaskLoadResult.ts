/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { EmailTask } from './EmailTask';
import type { InboxTask } from './InboxTask';

export type EmailTaskLoadResult = {
    email_task: EmailTask;
    inbox_task?: InboxTask;
};

