/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SmartListArchiveArgs } from '../models/SmartListArchiveArgs';
import type { SmartListCreateArgs } from '../models/SmartListCreateArgs';
import type { SmartListCreateResult } from '../models/SmartListCreateResult';
import type { SmartListFindArgs } from '../models/SmartListFindArgs';
import type { SmartListFindResult } from '../models/SmartListFindResult';
import type { SmartListItemArchiveArgs } from '../models/SmartListItemArchiveArgs';
import type { SmartListItemCreateArgs } from '../models/SmartListItemCreateArgs';
import type { SmartListItemCreateResult } from '../models/SmartListItemCreateResult';
import type { SmartListItemLoadArgs } from '../models/SmartListItemLoadArgs';
import type { SmartListItemLoadResult } from '../models/SmartListItemLoadResult';
import type { SmartListItemRemoveArgs } from '../models/SmartListItemRemoveArgs';
import type { SmartListItemUpdateArgs } from '../models/SmartListItemUpdateArgs';
import type { SmartListLoadArgs } from '../models/SmartListLoadArgs';
import type { SmartListLoadResult } from '../models/SmartListLoadResult';
import type { SmartListRemoveArgs } from '../models/SmartListRemoveArgs';
import type { SmartListTagArchiveArgs } from '../models/SmartListTagArchiveArgs';
import type { SmartListTagCreateArgs } from '../models/SmartListTagCreateArgs';
import type { SmartListTagCreateResult } from '../models/SmartListTagCreateResult';
import type { SmartListTagLoadArgs } from '../models/SmartListTagLoadArgs';
import type { SmartListTagLoadResult } from '../models/SmartListTagLoadResult';
import type { SmartListTagRemoveArgs } from '../models/SmartListTagRemoveArgs';
import type { SmartListTagUpdateArgs } from '../models/SmartListTagUpdateArgs';
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
     * The command for archiving a smart list tag.
     * The command for archiving a smart list tag.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public smartListTagArchive(
        requestBody?: SmartListTagArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-tag-archive',
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
     * The command for creating a smart list tag.
     * The command for creating a smart list tag.
     * @param requestBody The input data
     * @returns SmartListTagCreateResult Successful response
     * @throws ApiError
     */
    public smartListTagCreate(
        requestBody?: SmartListTagCreateArgs,
    ): CancelablePromise<SmartListTagCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-tag-create',
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
     * Use case for loading a smart list tag.
     * Use case for loading a smart list tag.
     * @param requestBody The input data
     * @returns SmartListTagLoadResult Successful response
     * @throws ApiError
     */
    public smartListTagLoad(
        requestBody?: SmartListTagLoadArgs,
    ): CancelablePromise<SmartListTagLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-tag-load',
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
     * The command for removing a smart list tag.
     * The command for removing a smart list tag.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public smartListTagRemove(
        requestBody?: SmartListTagRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-tag-remove',
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
     * The command for updating a smart list tag.
     * The command for updating a smart list tag.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public smartListTagUpdate(
        requestBody?: SmartListTagUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list-tag-update',
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
