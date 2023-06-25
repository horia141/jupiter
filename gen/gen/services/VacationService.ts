/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { VacationArchiveArgs } from '../models/VacationArchiveArgs';
import type { VacationCreateArgs } from '../models/VacationCreateArgs';
import type { VacationCreateResult } from '../models/VacationCreateResult';
import type { VacationFindArgs } from '../models/VacationFindArgs';
import type { VacationFindResult } from '../models/VacationFindResult';
import type { VacationLoadArgs } from '../models/VacationLoadArgs';
import type { VacationLoadResult } from '../models/VacationLoadResult';
import type { VacationUpdateArgs } from '../models/VacationUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class VacationService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Create Vacation
     * Create a vacation.
     * @param requestBody
     * @returns VacationCreateResult Successful Response
     * @throws ApiError
     */
    public createVacation(
        requestBody: VacationCreateArgs,
    ): CancelablePromise<VacationCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/vacation/create',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Archive Vacation
     * Archive a vacation.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveVacation(
        requestBody: VacationArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/vacation/archive',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Vacation
     * Update a vacation.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateVacation(
        requestBody: VacationUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/vacation/update',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Load Vacation
     * Load all vacations, filtering by id.
     * @param requestBody
     * @returns VacationLoadResult Successful Response
     * @throws ApiError
     */
    public loadVacation(
        requestBody: VacationLoadArgs,
    ): CancelablePromise<VacationLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/vacation/load',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Find Vacation
     * Find all vacations, filtering by id.
     * @param requestBody
     * @returns VacationFindResult Successful Response
     * @throws ApiError
     */
    public findVacation(
        requestBody: VacationFindArgs,
    ): CancelablePromise<VacationFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/vacation/find',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
