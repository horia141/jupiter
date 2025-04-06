/* generated using openapi-typescript-codegen -- do not edit */
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
import type { SlackTaskRemoveArgs } from '../models/SlackTaskRemoveArgs';
import type { SlackTaskUpdateArgs } from '../models/SlackTaskUpdateArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class SlackService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a slack task.
     * The command for archiving a slack task.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public slackTaskArchive(
        requestBody?: SlackTaskArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/slack-task-archive',
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
     * The command for updating the generation up project for slack tasks.
     * The command for updating the generation up project for slack tasks.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public slackTaskChangeGenerationProject(
        requestBody?: SlackTaskChangeGenerationProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/slack-task-change-generation-project',
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
     * The command for finding a slack task.
     * The command for finding a slack task.
     * @param requestBody The input data
     * @returns SlackTaskFindResult Successful response
     * @throws ApiError
     */
    public slackTaskFind(
        requestBody?: SlackTaskFindArgs,
    ): CancelablePromise<SlackTaskFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/slack-task-find',
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
     * Use case for loading a particular slack task.
     * Use case for loading a particular slack task.
     * @param requestBody The input data
     * @returns SlackTaskLoadResult Successful response
     * @throws ApiError
     */
    public slackTaskLoad(
        requestBody?: SlackTaskLoadArgs,
    ): CancelablePromise<SlackTaskLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/slack-task-load',
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
     * The command for loading the settings around slack tasks.
     * The command for loading the settings around slack tasks.
     * @param requestBody The input data
     * @returns SlackTaskLoadSettingsResult Successful response
     * @throws ApiError
     */
    public slackTaskLoadSettings(
        requestBody?: SlackTaskLoadSettingsArgs,
    ): CancelablePromise<SlackTaskLoadSettingsResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/slack-task-load-settings',
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
     * The command for archiving a slack task.
     * The command for archiving a slack task.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public slackTaskRemove(
        requestBody?: SlackTaskRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/slack-task-remove',
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
     * The command for updating a slack task.
     * The command for updating a slack task.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public slackTaskUpdate(
        requestBody?: SlackTaskUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/slack-task-update',
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
