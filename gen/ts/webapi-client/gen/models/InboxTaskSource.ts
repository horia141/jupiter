/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * The origin of an inbox task.
 */
export enum InboxTaskSource {
    USER = 'user',
    WORKING_MEM_CLEANUP = 'working-mem-cleanup',
    HABIT = 'habit',
    CHORE = 'chore',
    BIG_PLAN = 'big-plan',
    JOURNAL = 'journal',
    METRIC = 'metric',
    PERSON_CATCH_UP = 'person-catch-up',
    PERSON_BIRTHDAY = 'person-birthday',
    SLACK_TASK = 'slack-task',
    EMAIL_TASK = 'email-task',
}
