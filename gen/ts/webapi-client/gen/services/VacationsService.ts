/* generated using openapi-typescript-codegen -- do not edit */
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
import type { VacationRemoveArgs } from '../models/VacationRemoveArgs';
import type { VacationUpdateArgs } from '../models/VacationUpdateArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class VacationsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a vacation.
     * The command for archiving a vacation.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public vacationArchive(
        requestBody?: VacationArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/vacation-archive',
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
     * The command for creating a vacation.
     * The command for creating a vacation.
     * @param requestBody The input data
     * @returns VacationCreateResult Successful response
     * @throws ApiError
     */
    public vacationCreate(
        requestBody?: VacationCreateArgs,
    ): CancelablePromise<VacationCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/vacation-create',
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
     * The command for finding vacations.
     * The command for finding vacations.
     * @param requestBody The input data
     * @returns VacationFindResult Successful response
     * @throws ApiError
     */
    public vacationFind(
        requestBody?: VacationFindArgs,
    ): CancelablePromise<VacationFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/vacation-find',
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
     * Use case for loading a particular vacation.
     * Use case for loading a particular vacation.
     * @param requestBody The input data
     * @returns VacationLoadResult Successful response
     * @throws ApiError
     */
    public vacationLoad(
        requestBody?: VacationLoadArgs,
    ): CancelablePromise<VacationLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/vacation-load',
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
     * The command for removing a vacation.
     * The command for removing a vacation.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public vacationRemove(
        requestBody?: VacationRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/vacation-remove',
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
     * The command for updating a vacation's properties.
     * The command for updating a vacation's properties.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public vacationUpdate(
        requestBody?: VacationUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/vacation-update',
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
