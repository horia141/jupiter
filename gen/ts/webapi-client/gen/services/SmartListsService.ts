/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SmartListArchiveArgs } from '../models/SmartListArchiveArgs';
import type { SmartListCreateArgs } from '../models/SmartListCreateArgs';
import type { SmartListCreateResult } from '../models/SmartListCreateResult';
import type { SmartListFindArgs } from '../models/SmartListFindArgs';
import type { SmartListFindResult } from '../models/SmartListFindResult';
import type { SmartListLoadArgs } from '../models/SmartListLoadArgs';
import type { SmartListLoadResult } from '../models/SmartListLoadResult';
import type { SmartListRemoveArgs } from '../models/SmartListRemoveArgs';
import type { SmartListUpdateArgs } from '../models/SmartListUpdateArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class SmartListsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a smart list.
     * The command for archiving a smart list.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public smartListArchive(
        requestBody?: SmartListArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-archive',
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
     * The command for creating a smart list.
     * The command for creating a smart list.
     * @param requestBody The input data
     * @returns SmartListCreateResult Successful response
     * @throws ApiError
     */
    public smartListCreate(
        requestBody?: SmartListCreateArgs,
    ): CancelablePromise<SmartListCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-create',
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
     * The command for finding smart lists.
     * The command for finding smart lists.
     * @param requestBody The input data
     * @returns SmartListFindResult Successful response
     * @throws ApiError
     */
    public smartListFind(
        requestBody?: SmartListFindArgs,
    ): CancelablePromise<SmartListFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-find',
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
     * Use case for loading a smart list.
     * Use case for loading a smart list.
     * @param requestBody The input data
     * @returns SmartListLoadResult Successful response
     * @throws ApiError
     */
    public smartListLoad(
        requestBody?: SmartListLoadArgs,
    ): CancelablePromise<SmartListLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-load',
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
     * The command for removing a smart list.
     * The command for removing a smart list.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public smartListRemove(
        requestBody?: SmartListRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-remove',
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
     * The command for updating a smart list.
     * The command for updating a smart list.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public smartListUpdate(
        requestBody?: SmartListUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-update',
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
