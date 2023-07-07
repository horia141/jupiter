/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SlackTaskArchiveArgs } from '../models/SlackTaskArchiveArgs';
import type { SlackTaskChangeGenerationProjectArgs } from '../models/SlackTaskChangeGenerationProjectArgs';
import type { SlackTaskFindArgs } from '../models/SlackTaskFindArgs';
import type { SlackTaskFindResult } from '../models/SlackTaskFindResult';
import type { SlackTaskLoadArgs } from '../models/SlackTaskLoadArgs';
import type { SlackTaskLoadResult } from '../models/SlackTaskLoadResult';
import type { SlackTaskLoadSettingsArgs } from '../models/SlackTaskLoadSettingsArgs';
import type { SlackTaskLoadSettingsResult } from '../models/SlackTaskLoadSettingsResult';
import type { SlackTaskUpdateArgs } from '../models/SlackTaskUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class SlackTaskService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Archive Slack Task
     * Archive a slack task.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveSlackTask(
        requestBody: SlackTaskArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/slack-task/archive',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Slack Task
     * Update a slack task.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateSlackTask(
        requestBody: SlackTaskUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/slack-task/update',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Load Slack Task Settings
     * Change the project for a slack task.
     * @param requestBody
     * @returns SlackTaskLoadSettingsResult Successful Response
     * @throws ApiError
     */
    public loadSlackTaskSettings(
        requestBody: SlackTaskLoadSettingsArgs,
    ): CancelablePromise<SlackTaskLoadSettingsResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/slack-task/load-settings',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Change Slack Task Generation Project
     * Change the project for a slack task.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public changeSlackTaskGenerationProject(
        requestBody: SlackTaskChangeGenerationProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/slack-task/change-project',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Load Slack Task
     * Load a slack task.
     * @param requestBody
     * @returns SlackTaskLoadResult Successful Response
     * @throws ApiError
     */
    public loadSlackTask(
        requestBody: SlackTaskLoadArgs,
    ): CancelablePromise<SlackTaskLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/slack-task/load',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Find Slack Task
     * Find all slack tasks, filtering by id.
     * @param requestBody
     * @returns SlackTaskFindResult Successful Response
     * @throws ApiError
     */
    public findSlackTask(
        requestBody: SlackTaskFindArgs,
    ): CancelablePromise<SlackTaskFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/slack-task/find',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
