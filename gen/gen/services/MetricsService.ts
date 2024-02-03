/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MetricArchiveArgs } from '../models/MetricArchiveArgs';
import type { MetricChangeCollectionProjectArgs } from '../models/MetricChangeCollectionProjectArgs';
import type { MetricCreateArgs } from '../models/MetricCreateArgs';
import type { MetricCreateResult } from '../models/MetricCreateResult';
import type { MetricEntryArchiveArgs } from '../models/MetricEntryArchiveArgs';
import type { MetricEntryCreateArgs } from '../models/MetricEntryCreateArgs';
import type { MetricEntryCreateResult } from '../models/MetricEntryCreateResult';
import type { MetricEntryLoadArgs } from '../models/MetricEntryLoadArgs';
import type { MetricEntryLoadResult } from '../models/MetricEntryLoadResult';
import type { MetricEntryRemoveArgs } from '../models/MetricEntryRemoveArgs';
import type { MetricEntryUpdateArgs } from '../models/MetricEntryUpdateArgs';
import type { MetricFindArgs } from '../models/MetricFindArgs';
import type { MetricFindResult } from '../models/MetricFindResult';
import type { MetricLoadArgs } from '../models/MetricLoadArgs';
import type { MetricLoadResult } from '../models/MetricLoadResult';
import type { MetricLoadSettingsArgs } from '../models/MetricLoadSettingsArgs';
import type { MetricLoadSettingsResult } from '../models/MetricLoadSettingsResult';
import type { MetricRemoveArgs } from '../models/MetricRemoveArgs';
import type { MetricUpdateArgs } from '../models/MetricUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class MetricsService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * The command for archiving a metric.
     * The command for archiving a metric.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public metricArchive(
        requestBody: MetricArchiveArgs,
    ): CancelablePromise<null> {
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
     * @returns null Successful Response
     * @throws ApiError
     */
    public metricChangeCollectionProject(
        requestBody: MetricChangeCollectionProjectArgs,
    ): CancelablePromise<null> {
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
     * @returns MetricCreateResult Successful Response
     * @throws ApiError
     */
    public metricCreate(
        requestBody: MetricCreateArgs,
    ): CancelablePromise<MetricCreateResult> {
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
     * @returns null Successful Response
     * @throws ApiError
     */
    public metricEntryArchive(
        requestBody: MetricEntryArchiveArgs,
    ): CancelablePromise<null> {
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
     * @returns MetricEntryCreateResult Successful Response
     * @throws ApiError
     */
    public metricEntryCreate(
        requestBody: MetricEntryCreateArgs,
    ): CancelablePromise<MetricEntryCreateResult> {
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
     * @returns MetricEntryLoadResult Successful Response
     * @throws ApiError
     */
    public metricEntryLoad(
        requestBody: MetricEntryLoadArgs,
    ): CancelablePromise<MetricEntryLoadResult> {
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
     * @returns null Successful Response
     * @throws ApiError
     */
    public metricEntryRemove(
        requestBody: MetricEntryRemoveArgs,
    ): CancelablePromise<null> {
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
     * @returns null Successful Response
     * @throws ApiError
     */
    public metricEntryUpdate(
        requestBody: MetricEntryUpdateArgs,
    ): CancelablePromise<null> {
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
     * @returns MetricFindResult Successful Response
     * @throws ApiError
     */
    public metricFind(
        requestBody: MetricFindArgs,
    ): CancelablePromise<MetricFindResult> {
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
     * @returns MetricLoadResult Successful Response
     * @throws ApiError
     */
    public metricLoad(
        requestBody: MetricLoadArgs,
    ): CancelablePromise<MetricLoadResult> {
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
     * @returns MetricLoadSettingsResult Successful Response
     * @throws ApiError
     */
    public metricLoadSettings(
        requestBody: MetricLoadSettingsArgs,
    ): CancelablePromise<MetricLoadSettingsResult> {
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
     * @returns null Successful Response
     * @throws ApiError
     */
    public metricRemove(
        requestBody: MetricRemoveArgs,
    ): CancelablePromise<null> {
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
     * @returns null Successful Response
     * @throws ApiError
     */
    public metricUpdate(
        requestBody: MetricUpdateArgs,
    ): CancelablePromise<null> {
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
