/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChangePasswordArgs } from '../models/ChangePasswordArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class InboxTasksService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a inbox task.
     * The command for archiving a inbox task.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public inboxTaskArchive(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public inboxTaskAssociateWithBigPlan(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public inboxTaskChangeProject(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public inboxTaskCreate(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public inboxTaskFind(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public inboxTaskLoad(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public inboxTaskRemove(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public inboxTaskUpdate(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
