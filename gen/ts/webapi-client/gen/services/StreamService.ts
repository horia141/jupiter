/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ScheduleStreamArchiveArgs } from '../models/ScheduleStreamArchiveArgs';
import type { ScheduleStreamCreateForExternalIcalArgs } from '../models/ScheduleStreamCreateForExternalIcalArgs';
import type { ScheduleStreamCreateForExternalIcalResult } from '../models/ScheduleStreamCreateForExternalIcalResult';
import type { ScheduleStreamCreateForUserArgs } from '../models/ScheduleStreamCreateForUserArgs';
import type { ScheduleStreamCreateForUserResult } from '../models/ScheduleStreamCreateForUserResult';
import type { ScheduleStreamFindArgs } from '../models/ScheduleStreamFindArgs';
import type { ScheduleStreamFindResult } from '../models/ScheduleStreamFindResult';
import type { ScheduleStreamLoadArgs } from '../models/ScheduleStreamLoadArgs';
import type { ScheduleStreamLoadResult } from '../models/ScheduleStreamLoadResult';
import type { ScheduleStreamRemoveArgs } from '../models/ScheduleStreamRemoveArgs';
import type { ScheduleStreamUpdateArgs } from '../models/ScheduleStreamUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class StreamService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Use case for archiving a schedule stream.
     * Use case for archiving a schedule stream.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public scheduleStreamArchive(
        requestBody?: ScheduleStreamArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-stream-archive',
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
     * Use case for creating a schedule stream from an external iCal.
     * Use case for creating a schedule stream from an external iCal.
     * @param requestBody The input data
     * @returns ScheduleStreamCreateForExternalIcalResult Successful response
     * @throws ApiError
     */
    public scheduleStreamCreateForExternalIcal(
        requestBody?: ScheduleStreamCreateForExternalIcalArgs,
    ): CancelablePromise<ScheduleStreamCreateForExternalIcalResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-stream-create-for-external-ical',
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
     * Use case for creating a schedule stream.
     * Use case for creating a schedule stream.
     * @param requestBody The input data
     * @returns ScheduleStreamCreateForUserResult Successful response
     * @throws ApiError
     */
    public scheduleStreamCreateForUser(
        requestBody?: ScheduleStreamCreateForUserArgs,
    ): CancelablePromise<ScheduleStreamCreateForUserResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-stream-create-for-user',
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
     * Usecase for finding schedule streams.
     * Usecase for finding schedule streams.
     * @param requestBody The input data
     * @returns ScheduleStreamFindResult Successful response
     * @throws ApiError
     */
    public scheduleStreamFind(
        requestBody?: ScheduleStreamFindArgs,
    ): CancelablePromise<ScheduleStreamFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-stream-find',
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
     * Use case for loading a particular stream.
     * Use case for loading a particular stream.
     * @param requestBody The input data
     * @returns ScheduleStreamLoadResult Successful response
     * @throws ApiError
     */
    public scheduleStreamLoad(
        requestBody?: ScheduleStreamLoadArgs,
    ): CancelablePromise<ScheduleStreamLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-stream-load',
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
     * Use case for removing a schedule stream.
     * Use case for removing a schedule stream.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public scheduleStreamRemove(
        requestBody?: ScheduleStreamRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-stream-remove',
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
     * Use case for updating a schedule stream.
     * Use case for updating a schedule stream.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public scheduleStreamUpdate(
        requestBody?: ScheduleStreamUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-stream-update',
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
