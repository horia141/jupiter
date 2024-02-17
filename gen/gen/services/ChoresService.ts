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
import type { ChoreRemoveArgs } from '../models/ChoreRemoveArgs';
import type { ChoreSuspendArgs } from '../models/ChoreSuspendArgs';
import type { ChoreUnsuspendArgs } from '../models/ChoreUnsuspendArgs';
import type { ChoreUpdateArgs } from '../models/ChoreUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class ChoresService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * The command for archiving a chore.
     * The command for archiving a chore.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public choreArchive(
        requestBody?: ChoreArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore-archive',
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
     * The command for changing the project of a chore.
     * The command for changing the project of a chore.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public choreChangeProject(
        requestBody?: ChoreChangeProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore-change-project',
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
     * The command for creating a chore.
     * The command for creating a chore.
     * @param requestBody The input data
     * @returns ChoreCreateResult Successful response
     * @throws ApiError
     */
    public choreCreate(
        requestBody?: ChoreCreateArgs,
    ): CancelablePromise<ChoreCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore-create',
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
     * The command for finding a chore.
     * The command for finding a chore.
     * @param requestBody The input data
     * @returns ChoreFindResult Successful response
     * @throws ApiError
     */
    public choreFind(
        requestBody?: ChoreFindArgs,
    ): CancelablePromise<ChoreFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore-find',
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
     * Use case for loading a particular chore.
     * Use case for loading a particular chore.
     * @param requestBody The input data
     * @returns ChoreLoadResult Successful response
     * @throws ApiError
     */
    public choreLoad(
        requestBody?: ChoreLoadArgs,
    ): CancelablePromise<ChoreLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore-load',
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
     * The command for removing a chore.
     * The command for removing a chore.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public choreRemove(
        requestBody?: ChoreRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore-remove',
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
     * The command for suspending a chore.
     * The command for suspending a chore.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public choreSuspend(
        requestBody?: ChoreSuspendArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore-suspend',
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
     * The command for unsuspending a chore.
     * The command for unsuspending a chore.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public choreUnsuspend(
        requestBody?: ChoreUnsuspendArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore-unsuspend',
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
     * The command for updating a chore.
     * The command for updating a chore.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public choreUpdate(
        requestBody?: ChoreUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/chore-update',
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
