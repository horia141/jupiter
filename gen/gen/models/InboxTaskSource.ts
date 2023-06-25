/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * The origin of an inbox task.
 */
export enum InboxTaskSource {
    USER = 'user',
    BIG_PLAN = 'big-plan',
    HABIT = 'habit',
    CHORE = 'chore',
    METRIC = 'metric',
    PERSON_CATCH_UP = 'person-catch-up',
    PERSON_BIRTHDAY = 'person-birthday',
    SLACK_TASK = 'slack-task',
    EMAIL_TASK = 'email-task',
}
