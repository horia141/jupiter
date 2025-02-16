/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkingMemArchiveArgs } from '../models/WorkingMemArchiveArgs';
import type { WorkingMemChangeCleanUpProjectArgs } from '../models/WorkingMemChangeCleanUpProjectArgs';
import type { WorkingMemChangeGenerationPeriodArgs } from '../models/WorkingMemChangeGenerationPeriodArgs';
import type { WorkingMemFindArgs } from '../models/WorkingMemFindArgs';
import type { WorkingMemFindResult } from '../models/WorkingMemFindResult';
import type { WorkingMemLoadArgs } from '../models/WorkingMemLoadArgs';
import type { WorkingMemLoadCurrentArgs } from '../models/WorkingMemLoadCurrentArgs';
import type { WorkingMemLoadCurrentResult } from '../models/WorkingMemLoadCurrentResult';
import type { WorkingMemLoadResult } from '../models/WorkingMemLoadResult';
import type { WorkingMemLoadSettingsArgs } from '../models/WorkingMemLoadSettingsArgs';
import type { WorkingMemLoadSettingsResult } from '../models/WorkingMemLoadSettingsResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class WorkingMemService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * The command for archiving a working mem.
     * The command for archiving a working mem.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public workingMemArchive(
        requestBody?: WorkingMemArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/working-mem-archive',
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
     * The command for updating the collection up project for working mem.
     * The command for updating the collection up project for working mem.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public workingMemChangeCleanUpProject(
        requestBody?: WorkingMemChangeCleanUpProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/working-mem-change-clean-up-project',
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
     * The command for updating the generation period for working mem.
     * The command for updating the generation period for working mem.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public workingMemChangeGenerationPeriod(
        requestBody?: WorkingMemChangeGenerationPeriodArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/working-mem-change-generation-period',
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
     * The command for finding working mems.
     * The command for finding working mems.
     * @param requestBody The input data
     * @returns WorkingMemFindResult Successful response
     * @throws ApiError
     */
    public workingMemFind(
        requestBody?: WorkingMemFindArgs,
    ): CancelablePromise<WorkingMemFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/working-mem-find',
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
     * The command for loading the working mem.
     * The command for loading the working mem.
     * @param requestBody The input data
     * @returns WorkingMemLoadResult Successful response
     * @throws ApiError
     */
    public workingMemLoad(
        requestBody?: WorkingMemLoadArgs,
    ): CancelablePromise<WorkingMemLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/working-mem-load',
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
     * The command for loading the current working mem.
     * The command for loading the current working mem.
     * @param requestBody The input data
     * @returns WorkingMemLoadCurrentResult Successful response
     * @throws ApiError
     */
    public workingMemLoadCurrent(
        requestBody?: WorkingMemLoadCurrentArgs,
    ): CancelablePromise<WorkingMemLoadCurrentResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/working-mem-load-current',
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
     * The command for loading the settings around workingmem.
     * The command for loading the settings around workingmem.
     * @param requestBody The input data
     * @returns WorkingMemLoadSettingsResult Successful response
     * @throws ApiError
     */
    public workingMemLoadSettings(
        requestBody?: WorkingMemLoadSettingsArgs,
    ): CancelablePromise<WorkingMemLoadSettingsResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/working-mem-load-settings',
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
