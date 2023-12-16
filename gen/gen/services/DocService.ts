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
import type { DocUpdateArgs } from '../models/DocUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class DocService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Create Doc
     * Create a doc.
     * @param requestBody
     * @returns DocCreateResult Successful Response
     * @throws ApiError
     */
    public createDoc(
        requestBody: DocCreateArgs,
    ): CancelablePromise<DocCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/doc/create',
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
     * Archive Doc
     * Archive a doc.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveDoc(
        requestBody: DocArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/doc/archive',
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
     * Update Doc
     * Update a doc.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateDoc(
        requestBody: DocUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/doc/update',
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
     * Change Doc Parent
     * Change the parent for a doc.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public changeDocParent(
        requestBody: DocChangeParentArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/doc/change-parent',
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
     * Load Doc
     * Load a doc.
     * @param requestBody
     * @returns DocLoadResult Successful Response
     * @throws ApiError
     */
    public loadDoc(
        requestBody: DocLoadArgs,
    ): CancelablePromise<DocLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/doc/load',
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
     * Find Doc
     * Find all docs, filtering by id.
     * @param requestBody
     * @returns DocFindResult Successful Response
     * @throws ApiError
     */
    public findDoc(
        requestBody: DocFindArgs,
    ): CancelablePromise<DocFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/doc/find',
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
