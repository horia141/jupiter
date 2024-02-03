/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DocArchiveArgs } from '../models/DocArchiveArgs';
import type { DocChangeParentArgs } from '../models/DocChangeParentArgs';
import type { DocCreateArgs } from '../models/DocCreateArgs';
import type { DocCreateResult } from '../models/DocCreateResult';
import type { DocFindArgs } from '../models/DocFindArgs';
import type { DocFindResult } from '../models/DocFindResult';
import type { DocLoadArgs } from '../models/DocLoadArgs';
import type { DocLoadResult } from '../models/DocLoadResult';
import type { DocRemoveArgs } from '../models/DocRemoveArgs';
import type { DocUpdateArgs } from '../models/DocUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class DocsService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Use case for archiving a doc.
     * Use case for archiving a doc.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public docArchive(
        requestBody: DocArchiveArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/doc-archive',
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
     * The command for changing the parent for a doc .
     * The command for changing the parent for a doc .
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public docChangeParent(
        requestBody: DocChangeParentArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/doc-change-parent',
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
     * Use case for creating a doc.
     * Use case for creating a doc.
     * @param requestBody
     * @returns DocCreateResult Successful Response
     * @throws ApiError
     */
    public docCreate(
        requestBody: DocCreateArgs,
    ): CancelablePromise<DocCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/doc-create',
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
     * The use case for finding docs.
     * The use case for finding docs.
     * @param requestBody
     * @returns DocFindResult Successful Response
     * @throws ApiError
     */
    public docFind(
        requestBody: DocFindArgs,
    ): CancelablePromise<DocFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/doc-find',
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
     * Use case for loading a particular doc.
     * Use case for loading a particular doc.
     * @param requestBody
     * @returns DocLoadResult Successful Response
     * @throws ApiError
     */
    public docLoad(
        requestBody: DocLoadArgs,
    ): CancelablePromise<DocLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/doc-load',
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
     * The command for removing a doc.
     * The command for removing a doc.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public docRemove(
        requestBody: DocRemoveArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/doc-remove',
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
     * Update a doc use case.
     * Update a doc use case.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public docUpdate(
        requestBody: DocUpdateArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/doc-update',
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
