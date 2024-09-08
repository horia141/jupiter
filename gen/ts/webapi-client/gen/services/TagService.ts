/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SmartListTagArchiveArgs } from '../models/SmartListTagArchiveArgs';
import type { SmartListTagCreateArgs } from '../models/SmartListTagCreateArgs';
import type { SmartListTagCreateResult } from '../models/SmartListTagCreateResult';
import type { SmartListTagLoadArgs } from '../models/SmartListTagLoadArgs';
import type { SmartListTagLoadResult } from '../models/SmartListTagLoadResult';
import type { SmartListTagRemoveArgs } from '../models/SmartListTagRemoveArgs';
import type { SmartListTagUpdateArgs } from '../models/SmartListTagUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class TagService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

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

}
