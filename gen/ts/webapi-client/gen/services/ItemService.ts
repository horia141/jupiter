/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SmartListItemArchiveArgs } from '../models/SmartListItemArchiveArgs';
import type { SmartListItemCreateArgs } from '../models/SmartListItemCreateArgs';
import type { SmartListItemCreateResult } from '../models/SmartListItemCreateResult';
import type { SmartListItemLoadArgs } from '../models/SmartListItemLoadArgs';
import type { SmartListItemLoadResult } from '../models/SmartListItemLoadResult';
import type { SmartListItemRemoveArgs } from '../models/SmartListItemRemoveArgs';
import type { SmartListItemUpdateArgs } from '../models/SmartListItemUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class ItemService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * The command for archiving a smart list item.
     * The command for archiving a smart list item.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public smartListItemArchive(
        requestBody?: SmartListItemArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-item-archive',
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
     * The command for creating a smart list item.
     * The command for creating a smart list item.
     * @param requestBody The input data
     * @returns SmartListItemCreateResult Successful response
     * @throws ApiError
     */
    public smartListItemCreate(
        requestBody?: SmartListItemCreateArgs,
    ): CancelablePromise<SmartListItemCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-item-create',
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
     * Use case for loading a smart list item.
     * Use case for loading a smart list item.
     * @param requestBody The input data
     * @returns SmartListItemLoadResult Successful response
     * @throws ApiError
     */
    public smartListItemLoad(
        requestBody?: SmartListItemLoadArgs,
    ): CancelablePromise<SmartListItemLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-item-load',
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
     * The command for removing a smart list item.
     * The command for removing a smart list item.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public smartListItemRemove(
        requestBody?: SmartListItemRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-item-remove',
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
     * The command for updating a smart list item.
     * The command for updating a smart list item.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public smartListItemUpdate(
        requestBody?: SmartListItemUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-item-update',
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
