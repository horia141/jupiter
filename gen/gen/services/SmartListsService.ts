/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ModelSmartListCreateResult } from '../models/ModelSmartListCreateResult';
import type { ModelSmartListFindResult } from '../models/ModelSmartListFindResult';
import type { ModelSmartListItemCreateResult } from '../models/ModelSmartListItemCreateResult';
import type { ModelSmartListItemLoadResult } from '../models/ModelSmartListItemLoadResult';
import type { ModelSmartListLoadResult } from '../models/ModelSmartListLoadResult';
import type { ModelSmartListTagCreateResult } from '../models/ModelSmartListTagCreateResult';
import type { ModelSmartListTagLoadResult } from '../models/ModelSmartListTagLoadResult';
import type { SmartListArchiveArgs } from '../models/SmartListArchiveArgs';
import type { SmartListCreateArgs } from '../models/SmartListCreateArgs';
import type { SmartListFindArgs } from '../models/SmartListFindArgs';
import type { SmartListItemArchiveArgs } from '../models/SmartListItemArchiveArgs';
import type { SmartListItemCreateArgs } from '../models/SmartListItemCreateArgs';
import type { SmartListItemLoadArgs } from '../models/SmartListItemLoadArgs';
import type { SmartListItemRemoveArgs } from '../models/SmartListItemRemoveArgs';
import type { SmartListItemUpdateArgs } from '../models/SmartListItemUpdateArgs';
import type { SmartListLoadArgs } from '../models/SmartListLoadArgs';
import type { SmartListRemoveArgs } from '../models/SmartListRemoveArgs';
import type { SmartListTagArchiveArgs } from '../models/SmartListTagArchiveArgs';
import type { SmartListTagCreateArgs } from '../models/SmartListTagCreateArgs';
import type { SmartListTagLoadArgs } from '../models/SmartListTagLoadArgs';
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public smartListArchive(
        requestBody: SmartListArchiveArgs,
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
     * @param requestBody
     * @returns ModelSmartListCreateResult Successful Response
     * @throws ApiError
     */
    public smartListCreate(
        requestBody: SmartListCreateArgs,
    ): CancelablePromise<ModelSmartListCreateResult> {
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
     * @param requestBody
     * @returns ModelSmartListFindResult Successful Response
     * @throws ApiError
     */
    public smartListFind(
        requestBody: SmartListFindArgs,
    ): CancelablePromise<ModelSmartListFindResult> {
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public smartListItemArchive(
        requestBody: SmartListItemArchiveArgs,
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
     * @param requestBody
     * @returns ModelSmartListItemCreateResult Successful Response
     * @throws ApiError
     */
    public smartListItemCreate(
        requestBody: SmartListItemCreateArgs,
    ): CancelablePromise<ModelSmartListItemCreateResult> {
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
     * @param requestBody
     * @returns ModelSmartListItemLoadResult Successful Response
     * @throws ApiError
     */
    public smartListItemLoad(
        requestBody: SmartListItemLoadArgs,
    ): CancelablePromise<ModelSmartListItemLoadResult> {
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public smartListItemRemove(
        requestBody: SmartListItemRemoveArgs,
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public smartListItemUpdate(
        requestBody: SmartListItemUpdateArgs,
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
     * @param requestBody
     * @returns ModelSmartListLoadResult Successful Response
     * @throws ApiError
     */
    public smartListLoad(
        requestBody: SmartListLoadArgs,
    ): CancelablePromise<ModelSmartListLoadResult> {
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public smartListRemove(
        requestBody: SmartListRemoveArgs,
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public smartListTagArchive(
        requestBody: SmartListTagArchiveArgs,
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
     * @param requestBody
     * @returns ModelSmartListTagCreateResult Successful Response
     * @throws ApiError
     */
    public smartListTagCreate(
        requestBody: SmartListTagCreateArgs,
    ): CancelablePromise<ModelSmartListTagCreateResult> {
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
     * @param requestBody
     * @returns ModelSmartListTagLoadResult Successful Response
     * @throws ApiError
     */
    public smartListTagLoad(
        requestBody: SmartListTagLoadArgs,
    ): CancelablePromise<ModelSmartListTagLoadResult> {
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public smartListTagRemove(
        requestBody: SmartListTagRemoveArgs,
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public smartListTagUpdate(
        requestBody: SmartListTagUpdateArgs,
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
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public smartListUpdate(
        requestBody: SmartListUpdateArgs,
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
