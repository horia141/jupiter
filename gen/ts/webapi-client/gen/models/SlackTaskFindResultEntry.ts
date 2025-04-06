/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InboxTask } from './InboxTask';
import type { SlackTask } from './SlackTask';
/**
 * A single slack task result.
 */
export type SlackTaskFindResultEntry = {
    slack_task: SlackTask;
    inbox_task?: (InboxTask | null);
};

