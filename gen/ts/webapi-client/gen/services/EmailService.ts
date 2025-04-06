/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EmailTaskArchiveArgs } from '../models/EmailTaskArchiveArgs';
import type { EmailTaskChangeGenerationProjectArgs } from '../models/EmailTaskChangeGenerationProjectArgs';
import type { EmailTaskFindArgs } from '../models/EmailTaskFindArgs';
import type { EmailTaskFindResult } from '../models/EmailTaskFindResult';
import type { EmailTaskLoadArgs } from '../models/EmailTaskLoadArgs';
import type { EmailTaskLoadResult } from '../models/EmailTaskLoadResult';
import type { EmailTaskLoadSettingsArgs } from '../models/EmailTaskLoadSettingsArgs';
import type { EmailTaskLoadSettingsResult } from '../models/EmailTaskLoadSettingsResult';
import type { EmailTaskRemoveArgs } from '../models/EmailTaskRemoveArgs';
import type { EmailTaskUpdateArgs } from '../models/EmailTaskUpdateArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class EmailService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a email task.
     * The command for archiving a email task.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public emailTaskArchive(
        requestBody?: EmailTaskArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/email-task-archive',
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
     * The command for updating the generation up project for email tasks.
     * The command for updating the generation up project for email tasks.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public emailTaskChangeGenerationProject(
        requestBody?: EmailTaskChangeGenerationProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/email-task-change-generation-project',
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
     * The command for finding a email task.
     * The command for finding a email task.
     * @param requestBody The input data
     * @returns EmailTaskFindResult Successful response
     * @throws ApiError
     */
    public emailTaskFind(
        requestBody?: EmailTaskFindArgs,
    ): CancelablePromise<EmailTaskFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/email-task-find',
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
     * Use case for loading a particular email task.
     * Use case for loading a particular email task.
     * @param requestBody The input data
     * @returns EmailTaskLoadResult Successful response
     * @throws ApiError
     */
    public emailTaskLoad(
        requestBody?: EmailTaskLoadArgs,
    ): CancelablePromise<EmailTaskLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/email-task-load',
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
     * The command for loading the settings around email tasks.
     * The command for loading the settings around email tasks.
     * @param requestBody The input data
     * @returns EmailTaskLoadSettingsResult Successful response
     * @throws ApiError
     */
    public emailTaskLoadSettings(
        requestBody?: EmailTaskLoadSettingsArgs,
    ): CancelablePromise<EmailTaskLoadSettingsResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/email-task-load-settings',
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
     * The command for archiving a email task.
     * The command for archiving a email task.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public emailTaskRemove(
        requestBody?: EmailTaskRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/email-task-remove',
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
     * The command for updating a email task.
     * The command for updating a email task.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public emailTaskUpdate(
        requestBody?: EmailTaskUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/email-task-update',
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
