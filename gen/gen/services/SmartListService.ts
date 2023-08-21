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
import type { SmartListItemUpdateArgs } from '../models/SmartListItemUpdateArgs';
import type { SmartListLoadArgs } from '../models/SmartListLoadArgs';
import type { SmartListLoadResult } from '../models/SmartListLoadResult';
import type { SmartListTagArchiveArgs } from '../models/SmartListTagArchiveArgs';
import type { SmartListTagCreateArgs } from '../models/SmartListTagCreateArgs';
import type { SmartListTagCreateResult } from '../models/SmartListTagCreateResult';
import type { SmartListTagLoadArgs } from '../models/SmartListTagLoadArgs';
import type { SmartListTagLoadResult } from '../models/SmartListTagLoadResult';
import type { SmartListTagUpdateArgs } from '../models/SmartListTagUpdateArgs';
import type { SmartListUpdateArgs } from '../models/SmartListUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class SmartListService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Create Smart List
     * Create a smart list.
     * @param requestBody
     * @returns SmartListCreateResult Successful Response
     * @throws ApiError
     */
    public createSmartList(
        requestBody: SmartListCreateArgs,
    ): CancelablePromise<SmartListCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list/create',
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
     * Archive Smart List
     * Archive a smart list.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveSmartList(
        requestBody: SmartListArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list/archive',
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
     * Update Smart List
     * Update a smart list.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateSmartList(
        requestBody: SmartListUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list/update',
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
     * Load Smart List
     * Load a smart list.
     * @param requestBody
     * @returns SmartListLoadResult Successful Response
     * @throws ApiError
     */
    public loadSmartList(
        requestBody: SmartListLoadArgs,
    ): CancelablePromise<SmartListLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list/load',
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
     * Find Smart List
     * Find all smart lists, filtering by id.
     * @param requestBody
     * @returns SmartListFindResult Successful Response
     * @throws ApiError
     */
    public findSmartList(
        requestBody: SmartListFindArgs,
    ): CancelablePromise<SmartListFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list/find',
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
     * Create Smart List Tag
     * Create a smart list tag.
     * @param requestBody
     * @returns SmartListTagCreateResult Successful Response
     * @throws ApiError
     */
    public createSmartListTag(
        requestBody: SmartListTagCreateArgs,
    ): CancelablePromise<SmartListTagCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list/tag/create',
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
     * Archive Smart List Tag
     * Archive a smart list tag.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveSmartListTag(
        requestBody: SmartListTagArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list/tag/archive',
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
     * Update Smart List Tag
     * Update a smart list tag.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateSmartListTag(
        requestBody: SmartListTagUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list/tag/update',
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
     * Load Smart List Tag
     * Load a smart list tag.
     * @param requestBody
     * @returns SmartListTagLoadResult Successful Response
     * @throws ApiError
     */
    public loadSmartListTag(
        requestBody: SmartListTagLoadArgs,
    ): CancelablePromise<SmartListTagLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list/tag/load',
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
     * Create Smart List Item
     * Create a smart list item.
     * @param requestBody
     * @returns SmartListItemCreateResult Successful Response
     * @throws ApiError
     */
    public createSmartListItem(
        requestBody: SmartListItemCreateArgs,
    ): CancelablePromise<SmartListItemCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list/item/create',
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
     * Archive Smart List Item
     * Archive a smart list item.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveSmartListItem(
        requestBody: SmartListItemArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list/item/archive',
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
     * Update Smart List Item
     * Update a smart list item.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateSmartListItem(
        requestBody: SmartListItemUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list/item/update',
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
     * Load Smart List Item
     * Load a smart list item.
     * @param requestBody
     * @returns SmartListItemLoadResult Successful Response
     * @throws ApiError
     */
    public loadSmartListItem(
        requestBody: SmartListItemLoadArgs,
    ): CancelablePromise<SmartListItemLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/smart-list/item/load',
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
