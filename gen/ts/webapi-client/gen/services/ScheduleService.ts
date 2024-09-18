/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ScheduleExternalSyncDoArgs } from '../models/ScheduleExternalSyncDoArgs';

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

}
