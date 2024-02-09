/* generated using openapi-typescript-codegen -- do no edit */
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
import type { InboxTaskRemoveArgs } from '../models/InboxTaskRemoveArgs';
import type { InboxTaskUpdateArgs } from '../models/InboxTaskUpdateArgs';
import type { InboxTaskUpdateResult } from '../models/InboxTaskUpdateResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class InboxTasksService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a inbox task.
     * The command for archiving a inbox task.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public inboxTaskArchive(
        requestBody: InboxTaskArchiveArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task-archive',
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
     * The command for associating a inbox task with a big plan.
     * The command for associating a inbox task with a big plan.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public inboxTaskAssociateWithBigPlan(
        requestBody: InboxTaskAssociateWithBigPlanArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task-associate-with-big-plan',
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
     * The command for changing the project of a inbox task.
     * The command for changing the project of a inbox task.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public inboxTaskChangeProject(
        requestBody: InboxTaskChangeProjectArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task-change-project',
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
     * The command for creating a inbox task.
     * The command for creating a inbox task.
     * @param requestBody
     * @returns InboxTaskCreateResult Successful Response
     * @throws ApiError
     */
    public inboxTaskCreate(
        requestBody: InboxTaskCreateArgs,
    ): CancelablePromise<InboxTaskCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task-create',
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
     * The command for finding a inbox task.
     * The command for finding a inbox task.
     * @param requestBody
     * @returns InboxTaskFindResult Successful Response
     * @throws ApiError
     */
    public inboxTaskFind(
        requestBody: InboxTaskFindArgs,
    ): CancelablePromise<InboxTaskFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task-find',
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
     * The use case for loading a particular inbox task.
     * The use case for loading a particular inbox task.
     * @param requestBody
     * @returns InboxTaskLoadResult Successful Response
     * @throws ApiError
     */
    public inboxTaskLoad(
        requestBody: InboxTaskLoadArgs,
    ): CancelablePromise<InboxTaskLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task-load',
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
     * The command for removing a inbox task.
     * The command for removing a inbox task.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public inboxTaskRemove(
        requestBody: InboxTaskRemoveArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task-remove',
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
     * The command for updating a inbox task.
     * The command for updating a inbox task.
     * @param requestBody
     * @returns InboxTaskUpdateResult Successful Response
     * @throws ApiError
     */
    public inboxTaskUpdate(
        requestBody: InboxTaskUpdateArgs,
    ): CancelablePromise<InboxTaskUpdateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/inbox-task-update',
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
