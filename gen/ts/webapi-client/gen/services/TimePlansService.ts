/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TimePlanArchiveArgs } from '../models/TimePlanArchiveArgs';
import type { TimePlanAssociateWithActivitiesArgs } from '../models/TimePlanAssociateWithActivitiesArgs';
import type { TimePlanAssociateWithActivitiesResult } from '../models/TimePlanAssociateWithActivitiesResult';
import type { TimePlanAssociateWithBigPlansArgs } from '../models/TimePlanAssociateWithBigPlansArgs';
import type { TimePlanAssociateWithBigPlansResult } from '../models/TimePlanAssociateWithBigPlansResult';
import type { TimePlanAssociateWithInboxTasksArgs } from '../models/TimePlanAssociateWithInboxTasksArgs';
import type { TimePlanAssociateWithInboxTasksResult } from '../models/TimePlanAssociateWithInboxTasksResult';
import type { TimePlanChangeTimeConfigArgs } from '../models/TimePlanChangeTimeConfigArgs';
import type { TimePlanCreateArgs } from '../models/TimePlanCreateArgs';
import type { TimePlanCreateResult } from '../models/TimePlanCreateResult';
import type { TimePlanFindArgs } from '../models/TimePlanFindArgs';
import type { TimePlanFindResult } from '../models/TimePlanFindResult';
import type { TimePlanGenForTimePlanArgs } from '../models/TimePlanGenForTimePlanArgs';
import type { TimePlanLoadArgs } from '../models/TimePlanLoadArgs';
import type { TimePlanLoadResult } from '../models/TimePlanLoadResult';
import type { TimePlanRemoveArgs } from '../models/TimePlanRemoveArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class TimePlansService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

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
     * Use case for creating activities starting from already existin activities.
     * Use case for creating activities starting from already existin activities.
     * @param requestBody The input data
     * @returns TimePlanAssociateWithActivitiesResult Successful response
     * @throws ApiError
     */
    public timePlanAssociateWithActivities(
        requestBody?: TimePlanAssociateWithActivitiesArgs,
    ): CancelablePromise<TimePlanAssociateWithActivitiesResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-associate-with-activities',
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
     * Use case for creating activities starting from big plans.
     * Use case for creating activities starting from big plans.
     * @param requestBody The input data
     * @returns TimePlanAssociateWithBigPlansResult Successful response
     * @throws ApiError
     */
    public timePlanAssociateWithBigPlans(
        requestBody?: TimePlanAssociateWithBigPlansArgs,
    ): CancelablePromise<TimePlanAssociateWithBigPlansResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-associate-with-big-plans',
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
     * Use case for creating activities starting from inbox tasks.
     * Use case for creating activities starting from inbox tasks.
     * @param requestBody The input data
     * @returns TimePlanAssociateWithInboxTasksResult Successful response
     * @throws ApiError
     */
    public timePlanAssociateWithInboxTasks(
        requestBody?: TimePlanAssociateWithInboxTasksArgs,
    ): CancelablePromise<TimePlanAssociateWithInboxTasksResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-associate-with-inbox-tasks',
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
     * The command for generating new tasks for a time plan.
     * The command for generating new tasks for a time plan.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public timePlanGenForTimePlan(
        requestBody?: TimePlanGenForTimePlanArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-plan-gen-for-time-plan',
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
