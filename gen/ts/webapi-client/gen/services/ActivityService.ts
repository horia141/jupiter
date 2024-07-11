/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TimePlanActivityArchiveArgs } from '../models/TimePlanActivityArchiveArgs';
import type { TimePlanActivityLoadArgs } from '../models/TimePlanActivityLoadArgs';
import type { TimePlanActivityLoadResult } from '../models/TimePlanActivityLoadResult';
import type { TimePlanActivityRemoveArgs } from '../models/TimePlanActivityRemoveArgs';
import type { TimePlanActivityUpdateArgs } from '../models/TimePlanActivityUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class ActivityService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Use case for archiving a time plan activity.
     * Use case for archiving a time plan activity.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public timePlanActivityArchive(
        requestBody?: TimePlanActivityArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-activity-archive',
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
     * Use case for loading a time plan activity activity.
     * Use case for loading a time plan activity activity.
     * @param requestBody The input data
     * @returns TimePlanActivityLoadResult Successful response
     * @throws ApiError
     */
    public timePlanActivityLoad(
        requestBody?: TimePlanActivityLoadArgs,
    ): CancelablePromise<TimePlanActivityLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-activity-load',
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
     * Use case for removing a time plan activity.
     * Use case for removing a time plan activity.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public timePlanActivityRemove(
        requestBody?: TimePlanActivityRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-activity-remove',
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
     * The command for updating a time plan activity.
     * The command for updating a time plan activity.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public timePlanActivityUpdate(
        requestBody?: TimePlanActivityUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-activity-update',
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
