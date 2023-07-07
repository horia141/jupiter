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
import type { EmailTaskUpdateArgs } from '../models/EmailTaskUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class EmailTaskService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Archive Email Task
     * Archive a email task.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveEmailTask(
        requestBody: EmailTaskArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/email-task/archive',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Email Task
     * Update a email task.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateEmailTask(
        requestBody: EmailTaskUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/email-task/update',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Load Email Task Settings
     * Change the project for a email task.
     * @param requestBody
     * @returns EmailTaskLoadSettingsResult Successful Response
     * @throws ApiError
     */
    public loadEmailTaskSettings(
        requestBody: EmailTaskLoadSettingsArgs,
    ): CancelablePromise<EmailTaskLoadSettingsResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/email-task/load-settings',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Change Email Task Generation Project
     * Change the project for a email task.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public changeEmailTaskGenerationProject(
        requestBody: EmailTaskChangeGenerationProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/email-task/change-project',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Load Email Task
     * Load an email task.
     * @param requestBody
     * @returns EmailTaskLoadResult Successful Response
     * @throws ApiError
     */
    public loadEmailTask(
        requestBody: EmailTaskLoadArgs,
    ): CancelablePromise<EmailTaskLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/email-task/load',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Find Email Task
     * Find all email tasks, filtering by id.
     * @param requestBody
     * @returns EmailTaskFindResult Successful Response
     * @throws ApiError
     */
    public findEmailTask(
        requestBody: EmailTaskFindArgs,
    ): CancelablePromise<EmailTaskFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/email-task/find',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
