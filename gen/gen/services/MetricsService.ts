/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChangePasswordArgs } from '../models/ChangePasswordArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class MetricsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a metric.
     * The command for archiving a metric.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricArchive(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric-archive',
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
     * The command for updating the collection up project for metrics.
     * The command for updating the collection up project for metrics.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricChangeCollectionProject(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric-change-collection-project',
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
     * The command for creating a metric.
     * The command for creating a metric.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricCreate(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric-create',
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
     * The command for archiving a metric entry.
     * The command for archiving a metric entry.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricEntryArchive(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric-entry-archive',
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
     * The command for creating a metric entry.
     * The command for creating a metric entry.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricEntryCreate(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric-entry-create',
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
     * Use case for loading a metric entry.
     * Use case for loading a metric entry.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricEntryLoad(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric-entry-load',
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
     * The command for removing a metric entry.
     * The command for removing a metric entry.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricEntryRemove(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric-entry-remove',
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
     * The command for updating a metric entry's properties.
     * The command for updating a metric entry's properties.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricEntryUpdate(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric-entry-update',
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
     * The command for finding metrics.
     * The command for finding metrics.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricFind(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric-find',
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
     * Use case for loading a metric.
     * Use case for loading a metric.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricLoad(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric-load',
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
     * The command for loading the settings around metrics.
     * The command for loading the settings around metrics.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricLoadSettings(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric-load-settings',
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
     * The command for removing a metric.
     * The command for removing a metric.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricRemove(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric-remove',
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
     * The command for updating a metric's properties.
     * The command for updating a metric's properties.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public metricUpdate(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric-update',
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
