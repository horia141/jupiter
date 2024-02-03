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

export class PushIntegrationsService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * The command for archiving a email task.
     * The command for archiving a email task.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public emailTaskArchive(
        requestBody: EmailTaskArchiveArgs,
    ): CancelablePromise<null> {
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
     * @returns null Successful Response
     * @throws ApiError
     */
    public emailTaskChangeGenerationProject(
        requestBody: EmailTaskChangeGenerationProjectArgs,
    ): CancelablePromise<null> {
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
     * @returns EmailTaskFindResult Successful Response
     * @throws ApiError
     */
    public emailTaskFind(
        requestBody: EmailTaskFindArgs,
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
     * @param requestBody
     * @returns EmailTaskLoadResult Successful Response
     * @throws ApiError
     */
    public emailTaskLoad(
        requestBody: EmailTaskLoadArgs,
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
     * @param requestBody
     * @returns EmailTaskLoadSettingsResult Successful Response
     * @throws ApiError
     */
    public emailTaskLoadSettings(
        requestBody: EmailTaskLoadSettingsArgs,
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
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public emailTaskRemove(
        requestBody: EmailTaskRemoveArgs,
    ): CancelablePromise<null> {
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
     * @returns null Successful Response
     * @throws ApiError
     */
    public emailTaskUpdate(
        requestBody: EmailTaskUpdateArgs,
    ): CancelablePromise<null> {
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
     * @returns null Successful Response
     * @throws ApiError
     */
    public slackTaskArchive(
        requestBody: SlackTaskArchiveArgs,
    ): CancelablePromise<null> {
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
     * @returns null Successful Response
     * @throws ApiError
     */
    public slackTaskChangeGenerationProject(
        requestBody: SlackTaskChangeGenerationProjectArgs,
    ): CancelablePromise<null> {
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
     * @returns SlackTaskFindResult Successful Response
     * @throws ApiError
     */
    public slackTaskFind(
        requestBody: SlackTaskFindArgs,
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
     * @param requestBody
     * @returns SlackTaskLoadResult Successful Response
     * @throws ApiError
     */
    public slackTaskLoad(
        requestBody: SlackTaskLoadArgs,
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
     * @param requestBody
     * @returns SlackTaskLoadSettingsResult Successful Response
     * @throws ApiError
     */
    public slackTaskLoadSettings(
        requestBody: SlackTaskLoadSettingsArgs,
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
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public slackTaskRemove(
        requestBody: SlackTaskRemoveArgs,
    ): CancelablePromise<null> {
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
     * @returns null Successful Response
     * @throws ApiError
     */
    public slackTaskUpdate(
        requestBody: SlackTaskUpdateArgs,
    ): CancelablePromise<null> {
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
