/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InboxTaskArchiveArgs } from '../models/InboxTaskArchiveArgs';
import type { InboxTaskAssociateWithBigPlanArgs } from '../models/InboxTaskAssociateWithBigPlanArgs';
import type { InboxTaskChangeProjectArgs } from '../models/InboxTaskChangeProjectArgs';
import type { InboxTaskCreateArgs } from '../models/InboxTaskCreateArgs';
import type { InboxTaskCreateResult } from '../models/InboxTaskCreateResult';
import type { InboxTaskFindArgs } from '../models/InboxTaskFindArgs';
import type { InboxTaskFindResult } from '../models/InboxTaskFindResult';
import type { InboxTaskLoadArgs } from '../models/InboxTaskLoadArgs';
import type { InboxTaskLoadResult } from '../models/InboxTaskLoadResult';
import type { InboxTaskUpdateArgs } from '../models/InboxTaskUpdateArgs';
import type { InboxTaskUpdateResult } from '../models/InboxTaskUpdateResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class InboxTaskService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Create Inbox Task
     * Create a inbox task.
     * @param requestBody
     * @returns InboxTaskCreateResult Successful Response
     * @throws ApiError
     */
    public createInboxTask(
        requestBody: InboxTaskCreateArgs,
    ): CancelablePromise<InboxTaskCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task/create',
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
     * Archive Inbox Task
     * Archive a inbox task.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveInboxTask(
        requestBody: InboxTaskArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task/archive',
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
     * Update Inbox Task
     * Update a inbox task.
     * @param requestBody
     * @returns InboxTaskUpdateResult Successful Response
     * @throws ApiError
     */
    public updateInboxTask(
        requestBody: InboxTaskUpdateArgs,
    ): CancelablePromise<InboxTaskUpdateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task/update',
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
     * Change Inbox Task Project
     * Change the project for a inbox task.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public changeInboxTaskProject(
        requestBody: InboxTaskChangeProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task/change-project',
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
     * Associate Inbox Task With Big Plan
     * Change the inbox task for a project.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public associateInboxTaskWithBigPlan(
        requestBody: InboxTaskAssociateWithBigPlanArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task/associate-with-big-plan',
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
     * Load Inbox Task
     * Load a inbox task.
     * @param requestBody
     * @returns InboxTaskLoadResult Successful Response
     * @throws ApiError
     */
    public loadInboxTask(
        requestBody: InboxTaskLoadArgs,
    ): CancelablePromise<InboxTaskLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task/load',
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
     * Find Inbox Task
     * Find all inbox tasks, filtering by id.
     * @param requestBody
     * @returns InboxTaskFindResult Successful Response
     * @throws ApiError
     */
    public findInboxTask(
        requestBody: InboxTaskFindArgs,
    ): CancelablePromise<InboxTaskFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task/find',
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
