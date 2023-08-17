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
import type { MetricEntryUpdateArgs } from '../models/MetricEntryUpdateArgs';
import type { MetricFindArgs } from '../models/MetricFindArgs';
import type { MetricFindResult } from '../models/MetricFindResult';
import type { MetricLoadArgs } from '../models/MetricLoadArgs';
import type { MetricLoadResult } from '../models/MetricLoadResult';
import type { MetricLoadSettingsArgs } from '../models/MetricLoadSettingsArgs';
import type { MetricLoadSettingsResult } from '../models/MetricLoadSettingsResult';
import type { MetricUpdateArgs } from '../models/MetricUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class MetricService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Create Metric
     * Create a metric.
     * @param requestBody
     * @returns MetricCreateResult Successful Response
     * @throws ApiError
     */
    public createMetric(
        requestBody: MetricCreateArgs,
    ): CancelablePromise<MetricCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric/create',
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
     * Archive Metric
     * Archive a metric.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveMetric(
        requestBody: MetricArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric/archive',
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
     * Update Metric
     * Update a metric.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateMetric(
        requestBody: MetricUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric/update',
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
     * Load Metric Settings
     * Load settings for metrics.
     * @param requestBody
     * @returns MetricLoadSettingsResult Successful Response
     * @throws ApiError
     */
    public loadMetricSettings(
        requestBody: MetricLoadSettingsArgs,
    ): CancelablePromise<MetricLoadSettingsResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric/load-settings',
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
     * Change Metric Collection Project
     * Change the collection project for metric.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public changeMetricCollectionProject(
        requestBody: MetricChangeCollectionProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric/change-collection-project',
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
     * Load Metric
     * Load a metric.
     * @param requestBody
     * @returns MetricLoadResult Successful Response
     * @throws ApiError
     */
    public loadMetric(
        requestBody: MetricLoadArgs,
    ): CancelablePromise<MetricLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric/load',
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
     * Find Metric
     * Find all metrics, filtering by id.
     * @param requestBody
     * @returns MetricFindResult Successful Response
     * @throws ApiError
     */
    public findMetric(
        requestBody: MetricFindArgs,
    ): CancelablePromise<MetricFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric/find',
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
     * Create Metric Entry
     * Create a metric entry.
     * @param requestBody
     * @returns MetricEntryCreateResult Successful Response
     * @throws ApiError
     */
    public createMetricEntry(
        requestBody: MetricEntryCreateArgs,
    ): CancelablePromise<MetricEntryCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric/entry/create',
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
     * Archive Metric Entry
     * Archive a metric entry.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveMetricEntry(
        requestBody: MetricEntryArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric/entry/archive',
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
     * Update Metric Entry
     * Update a metric entry.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateMetricEntry(
        requestBody: MetricEntryUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric/entry/update',
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
     * Load Metric Entry
     * Load a metric entry.
     * @param requestBody
     * @returns MetricEntryLoadResult Successful Response
     * @throws ApiError
     */
    public loadMetricEntry(
        requestBody: MetricEntryLoadArgs,
    ): CancelablePromise<MetricEntryLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/metric/entry/load',
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
