/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * The source of the modification which this event records.
 */
export enum EventSource {
    CLI = 'cli',
    WEB = 'web',
    SLACK = 'slack',
    EMAIL = 'email',
    GC_CRON = 'gc-cron',
    GEN_CRON = 'gen-cron',
    SCHEDULE_EXTERNAL_SYNC_CRON = 'schedule-external-sync-cron',
}
