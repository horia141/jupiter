/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HomeTabArchiveArgs } from '../models/HomeTabArchiveArgs';
import type { HomeTabCreateArgs } from '../models/HomeTabCreateArgs';
import type { HomeTabCreateResult } from '../models/HomeTabCreateResult';
import type { HomeTabLoadArgs } from '../models/HomeTabLoadArgs';
import type { HomeTabLoadResult } from '../models/HomeTabLoadResult';
import type { HomeTabRemoveArgs } from '../models/HomeTabRemoveArgs';
import type { HomeTabUpdateArgs } from '../models/HomeTabUpdateArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class TabService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a home tab.
     * The command for archiving a home tab.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public homeTabArchive(
        requestBody?: HomeTabArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/home-tab-archive',
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
     * The use case for creating a home tab.
     * The use case for creating a home tab.
     * @param requestBody The input data
     * @returns HomeTabCreateResult Successful response
     * @throws ApiError
     */
    public homeTabCreate(
        requestBody?: HomeTabCreateArgs,
    ): CancelablePromise<HomeTabCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/home-tab-create',
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
     * The use case for loading a home tab.
     * The use case for loading a home tab.
     * @param requestBody The input data
     * @returns HomeTabLoadResult Successful response
     * @throws ApiError
     */
    public homeTabLoad(
        requestBody?: HomeTabLoadArgs,
    ): CancelablePromise<HomeTabLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/home-tab-load',
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
     * The command for archiving a home tab.
     * The command for archiving a home tab.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public homeTabRemove(
        requestBody?: HomeTabRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/home-tab-remove',
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
     * The command for updating a home tab's properties.
     * The command for updating a home tab's properties.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public homeTabUpdate(
        requestBody?: HomeTabUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/home-tab-update',
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
