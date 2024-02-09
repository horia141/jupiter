/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EmailTaskArchiveArgs } from '../models/EmailTaskArchiveArgs';
import type { EmailTaskChangeGenerationProjectArgs } from '../models/EmailTaskChangeGenerationProjectArgs';
import type { EmailTaskFindArgs } from '../models/EmailTaskFindArgs';
import type { EmailTaskLoadArgs } from '../models/EmailTaskLoadArgs';
import type { EmailTaskLoadSettingsArgs } from '../models/EmailTaskLoadSettingsArgs';
import type { EmailTaskRemoveArgs } from '../models/EmailTaskRemoveArgs';
import type { EmailTaskUpdateArgs } from '../models/EmailTaskUpdateArgs';
import type { ModelEmailTaskFindResult } from '../models/ModelEmailTaskFindResult';
import type { ModelEmailTaskLoadResult } from '../models/ModelEmailTaskLoadResult';
import type { ModelEmailTaskLoadSettingsResult } from '../models/ModelEmailTaskLoadSettingsResult';
import type { ModelSlackTaskFindResult } from '../models/ModelSlackTaskFindResult';
import type { ModelSlackTaskLoadResult } from '../models/ModelSlackTaskLoadResult';
import type { ModelSlackTaskLoadSettingsResult } from '../models/ModelSlackTaskLoadSettingsResult';
import type { SlackTaskArchiveArgs } from '../models/SlackTaskArchiveArgs';
import type { SlackTaskChangeGenerationProjectArgs } from '../models/SlackTaskChangeGenerationProjectArgs';
import type { SlackTaskFindArgs } from '../models/SlackTaskFindArgs';
import type { SlackTaskLoadArgs } from '../models/SlackTaskLoadArgs';
import type { SlackTaskLoadSettingsArgs } from '../models/SlackTaskLoadSettingsArgs';
import type { SlackTaskRemoveArgs } from '../models/SlackTaskRemoveArgs';
import type { SlackTaskUpdateArgs } from '../models/SlackTaskUpdateArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class PushIntegrationsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a email task.
     * The command for archiving a email task.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public emailTaskArchive(
        requestBody: EmailTaskArchiveArgs,
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public emailTaskChangeGenerationProject(
        requestBody: EmailTaskChangeGenerationProjectArgs,
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
     * @param requestBody
     * @returns ModelEmailTaskFindResult Successful Response
     * @throws ApiError
     */
    public emailTaskFind(
        requestBody: EmailTaskFindArgs,
    ): CancelablePromise<ModelEmailTaskFindResult> {
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
     * @param requestBody
     * @returns ModelEmailTaskLoadResult Successful Response
     * @throws ApiError
     */
    public emailTaskLoad(
        requestBody: EmailTaskLoadArgs,
    ): CancelablePromise<ModelEmailTaskLoadResult> {
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
     * @param requestBody
     * @returns ModelEmailTaskLoadSettingsResult Successful Response
     * @throws ApiError
     */
    public emailTaskLoadSettings(
        requestBody: EmailTaskLoadSettingsArgs,
    ): CancelablePromise<ModelEmailTaskLoadSettingsResult> {
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public emailTaskRemove(
        requestBody: EmailTaskRemoveArgs,
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public emailTaskUpdate(
        requestBody: EmailTaskUpdateArgs,
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
    /**
     * The command for archiving a slack task.
     * The command for archiving a slack task.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public slackTaskArchive(
        requestBody: SlackTaskArchiveArgs,
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public slackTaskChangeGenerationProject(
        requestBody: SlackTaskChangeGenerationProjectArgs,
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
     * @param requestBody
     * @returns ModelSlackTaskFindResult Successful Response
     * @throws ApiError
     */
    public slackTaskFind(
        requestBody: SlackTaskFindArgs,
    ): CancelablePromise<ModelSlackTaskFindResult> {
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
     * @param requestBody
     * @returns ModelSlackTaskLoadResult Successful Response
     * @throws ApiError
     */
    public slackTaskLoad(
        requestBody: SlackTaskLoadArgs,
    ): CancelablePromise<ModelSlackTaskLoadResult> {
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
     * @param requestBody
     * @returns ModelSlackTaskLoadSettingsResult Successful Response
     * @throws ApiError
     */
    public slackTaskLoadSettings(
        requestBody: SlackTaskLoadSettingsArgs,
    ): CancelablePromise<ModelSlackTaskLoadSettingsResult> {
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public slackTaskRemove(
        requestBody: SlackTaskRemoveArgs,
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public slackTaskUpdate(
        requestBody: SlackTaskUpdateArgs,
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
