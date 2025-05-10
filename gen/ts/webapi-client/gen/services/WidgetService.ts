/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HomeWidgetArchiveArgs } from '../models/HomeWidgetArchiveArgs';
import type { HomeWidgetCreateArgs } from '../models/HomeWidgetCreateArgs';
import type { HomeWidgetLoadArgs } from '../models/HomeWidgetLoadArgs';
import type { HomeWidgetLoadResult } from '../models/HomeWidgetLoadResult';
import type { HomeWidgetMoveAndResizeArgs } from '../models/HomeWidgetMoveAndResizeArgs';
import type { HomeWidgetRemoveArgs } from '../models/HomeWidgetRemoveArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class WidgetService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The use case for archiving a home widget.
     * The use case for archiving a home widget.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public homeWidgetArchive(
        requestBody?: HomeWidgetArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/home-widget-archive',
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
     * The use case for creating a home small screen widget.
     * The use case for creating a home small screen widget.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public homeWidgetCreate(
        requestBody?: HomeWidgetCreateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/home-widget-create',
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
     * The use case for loading a home widget.
     * The use case for loading a home widget.
     * @param requestBody The input data
     * @returns HomeWidgetLoadResult Successful response
     * @throws ApiError
     */
    public homeWidgetLoad(
        requestBody?: HomeWidgetLoadArgs,
    ): CancelablePromise<HomeWidgetLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/home-widget-load',
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
     * The use case for moving a home widget.
     * The use case for moving a home widget.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public homeWidgetMoveAndResize(
        requestBody?: HomeWidgetMoveAndResizeArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/home-widget-move-and-resize',
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
     * The use case for removing a home widget.
     * The use case for removing a home widget.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public homeWidgetRemove(
        requestBody?: HomeWidgetRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/home-widget-remove',
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
