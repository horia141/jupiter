/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { InboxTask } from './InboxTask';

/**
 * The result of the archive operation.
 */
export type BigPlanArchiveServiceResult = {
    archived_inbox_tasks: Array<InboxTask>;
};

