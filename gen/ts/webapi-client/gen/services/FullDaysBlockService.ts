/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TimeEventFullDaysBlockLoadArgs } from '../models/TimeEventFullDaysBlockLoadArgs';
import type { TimeEventFullDaysBlockLoadResult } from '../models/TimeEventFullDaysBlockLoadResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class FullDaysBlockService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Load a full day block and associated data.
     * Load a full day block and associated data.
     * @param requestBody The input data
     * @returns TimeEventFullDaysBlockLoadResult Successful response
     * @throws ApiError
     */
    public timeEventFullDaysBlockLoad(
        requestBody?: TimeEventFullDaysBlockLoadArgs,
    ): CancelablePromise<TimeEventFullDaysBlockLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-event-full-days-block-load',
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
