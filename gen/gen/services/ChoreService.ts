/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChoreArchiveArgs } from '../models/ChoreArchiveArgs';
import type { ChoreChangeProjectArgs } from '../models/ChoreChangeProjectArgs';
import type { ChoreCreateArgs } from '../models/ChoreCreateArgs';
import type { ChoreCreateResult } from '../models/ChoreCreateResult';
import type { ChoreFindArgs } from '../models/ChoreFindArgs';
import type { ChoreFindResult } from '../models/ChoreFindResult';
import type { ChoreLoadArgs } from '../models/ChoreLoadArgs';
import type { ChoreLoadResult } from '../models/ChoreLoadResult';
import type { ChoreSuspendArgs } from '../models/ChoreSuspendArgs';
import type { ChoreUnsuspendArgs } from '../models/ChoreUnsuspendArgs';
import type { ChoreUpdateArgs } from '../models/ChoreUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class ChoreService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Create Chore
     * Create a chore.
     * @param requestBody
     * @returns ChoreCreateResult Successful Response
     * @throws ApiError
     */
    public createChore(
        requestBody: ChoreCreateArgs,
    ): CancelablePromise<ChoreCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore/create',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Archive Chore
     * Archive a chore.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveChore(
        requestBody: ChoreArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore/archive',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Chore
     * Update a chore.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateChore(
        requestBody: ChoreUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore/update',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Change Chore Project
     * Change the project for a chore.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public changeChoreProject(
        requestBody: ChoreChangeProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore/change-project',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Suspend Chore
     * Suspend a chore.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public suspendChore(
        requestBody: ChoreSuspendArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore/suspend',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Unsuspend Chore
     * Unsuspend a chore.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public unsuspendChore(
        requestBody: ChoreUnsuspendArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore/unsuspend',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Load Chore
     * Load a chore.
     * @param requestBody
     * @returns ChoreLoadResult Successful Response
     * @throws ApiError
     */
    public loadChore(
        requestBody: ChoreLoadArgs,
    ): CancelablePromise<ChoreLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore/load',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Find Chore
     * Find all chores, filtering by id..
     * @param requestBody
     * @returns ChoreFindResult Successful Response
     * @throws ApiError
     */
    public findChore(
        requestBody: ChoreFindArgs,
    ): CancelablePromise<ChoreFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore/find',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
