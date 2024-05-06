/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TimePlanActivityArchiveArgs } from '../models/TimePlanActivityArchiveArgs';
import type { TimePlanActivityCreateForBigPlanArgs } from '../models/TimePlanActivityCreateForBigPlanArgs';
import type { TimePlanActivityCreateForBigPlanResult } from '../models/TimePlanActivityCreateForBigPlanResult';
import type { TimePlanActivityCreateForInboxTaskArgs } from '../models/TimePlanActivityCreateForInboxTaskArgs';
import type { TimePlanActivityCreateForInboxTaskResult } from '../models/TimePlanActivityCreateForInboxTaskResult';
import type { TimePlanActivityUpdateArgs } from '../models/TimePlanActivityUpdateArgs';
import type { TimePlanArchiveArgs } from '../models/TimePlanArchiveArgs';
import type { TimePlanChangeTimeConfigArgs } from '../models/TimePlanChangeTimeConfigArgs';
import type { TimePlanCreateArgs } from '../models/TimePlanCreateArgs';
import type { TimePlanCreateResult } from '../models/TimePlanCreateResult';
import type { TimePlanFindArgs } from '../models/TimePlanFindArgs';
import type { TimePlanFindResult } from '../models/TimePlanFindResult';
import type { TimePlanLoadArgs } from '../models/TimePlanLoadArgs';
import type { TimePlanLoadResult } from '../models/TimePlanLoadResult';
import type { TimePlanRemoveArgs } from '../models/TimePlanRemoveArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class TimePlansService {

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
     * Use case for creating a time plan activity from a big plan.
     * Use case for creating a time plan activity from a big plan.
     * @param requestBody The input data
     * @returns TimePlanActivityCreateForBigPlanResult Successful response
     * @throws ApiError
     */
    public timePlanActivityCreateForBigPlan(
        requestBody?: TimePlanActivityCreateForBigPlanArgs,
    ): CancelablePromise<TimePlanActivityCreateForBigPlanResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-activity-create-for-big-plan',
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
     * Use case for creating a time plan from an inbox task.
     * Use case for creating a time plan from an inbox task.
     * @param requestBody The input data
     * @returns TimePlanActivityCreateForInboxTaskResult Successful response
     * @throws ApiError
     */
    public timePlanActivityCreateForInboxTask(
        requestBody?: TimePlanActivityCreateForInboxTaskArgs,
    ): CancelablePromise<TimePlanActivityCreateForInboxTaskResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-activity-create-for-inbox-task',
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

    /**
     * Use case for archiving a time plan.
     * Use case for archiving a time plan.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public timePlanArchive(
        requestBody?: TimePlanArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-archive',
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
     * Command for updating the time configuration of a time_plan.
     * Command for updating the time configuration of a time_plan.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public timePlanChangeTimeConfig(
        requestBody?: TimePlanChangeTimeConfigArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-change-time-config',
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
     * Use case for creating a time plan.
     * Use case for creating a time plan.
     * @param requestBody The input data
     * @returns TimePlanCreateResult Successful response
     * @throws ApiError
     */
    public timePlanCreate(
        requestBody?: TimePlanCreateArgs,
    ): CancelablePromise<TimePlanCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-create',
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
     * The command for finding time plans.
     * The command for finding time plans.
     * @param requestBody The input data
     * @returns TimePlanFindResult Successful response
     * @throws ApiError
     */
    public timePlanFind(
        requestBody?: TimePlanFindArgs,
    ): CancelablePromise<TimePlanFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-find',
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
     * The command for loading details about a time plan.
     * The command for loading details about a time plan.
     * @param requestBody The input data
     * @returns TimePlanLoadResult Successful response
     * @throws ApiError
     */
    public timePlanLoad(
        requestBody?: TimePlanLoadArgs,
    ): CancelablePromise<TimePlanLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-load',
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
     * Use case for removing a time_plan.
     * Use case for removing a time_plan.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public timePlanRemove(
        requestBody?: TimePlanRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-remove',
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
