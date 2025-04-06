/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ScheduleExternalSyncDoArgs } from '../models/ScheduleExternalSyncDoArgs';
import type { ScheduleExternalSyncLoadRunsArgs } from '../models/ScheduleExternalSyncLoadRunsArgs';
import type { ScheduleExternalSyncLoadRunsResult } from '../models/ScheduleExternalSyncLoadRunsResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class ScheduleService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for doing a sync.
     * The command for doing a sync.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public scheduleExternalSyncDo(
        requestBody?: ScheduleExternalSyncDoArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-external-sync-do',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                406: `Feature Not Available`,
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Use case for loading external sync runs.
     * Use case for loading external sync runs.
     * @param requestBody The input data
     * @returns ScheduleExternalSyncLoadRunsResult Successful response
     * @throws ApiError
     */
    public scheduleExternalSyncLoadRuns(
        requestBody?: ScheduleExternalSyncLoadRunsArgs,
    ): CancelablePromise<ScheduleExternalSyncLoadRunsResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-external-sync-load-runs',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                406: `Feature Not Available`,
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }
}
