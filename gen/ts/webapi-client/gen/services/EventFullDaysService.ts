/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ScheduleEventFullDaysArchiveArgs } from '../models/ScheduleEventFullDaysArchiveArgs';
import type { ScheduleEventFullDaysChangeScheduleStreamArgs } from '../models/ScheduleEventFullDaysChangeScheduleStreamArgs';
import type { ScheduleEventFullDaysCreateArgs } from '../models/ScheduleEventFullDaysCreateArgs';
import type { ScheduleEventFullDaysCreateResult } from '../models/ScheduleEventFullDaysCreateResult';
import type { ScheduleEventFullDaysLoadArgs } from '../models/ScheduleEventFullDaysLoadArgs';
import type { ScheduleEventFullDaysLoadResult } from '../models/ScheduleEventFullDaysLoadResult';
import type { ScheduleEventFullDaysRemoveArgs } from '../models/ScheduleEventFullDaysRemoveArgs';
import type { ScheduleEventFullDaysUpdateArgs } from '../models/ScheduleEventFullDaysUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class EventFullDaysService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Use case for archiving a schedule full day event.
     * Use case for archiving a schedule full day event.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public scheduleEventFullDaysArchive(
        requestBody?: ScheduleEventFullDaysArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-event-full-days-archive',
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
     * Use case for changing the schedule stream of an event.
     * Use case for changing the schedule stream of an event.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public scheduleEventFullDaysChangeScheduleStream(
        requestBody?: ScheduleEventFullDaysChangeScheduleStreamArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-event-full-days-change-schedule-stream',
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
     * Use case for creating a full day event in the schedule.
     * Use case for creating a full day event in the schedule.
     * @param requestBody The input data
     * @returns ScheduleEventFullDaysCreateResult Successful response
     * @throws ApiError
     */
    public scheduleEventFullDaysCreate(
        requestBody?: ScheduleEventFullDaysCreateArgs,
    ): CancelablePromise<ScheduleEventFullDaysCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-event-full-days-create',
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
     * Use case for loading a schedule full days event.
     * Use case for loading a schedule full days event.
     * @param requestBody The input data
     * @returns ScheduleEventFullDaysLoadResult Successful response
     * @throws ApiError
     */
    public scheduleEventFullDaysLoad(
        requestBody?: ScheduleEventFullDaysLoadArgs,
    ): CancelablePromise<ScheduleEventFullDaysLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-event-full-days-load',
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
     * Use case for removing a full day event.
     * Use case for removing a full day event.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public scheduleEventFullDaysRemove(
        requestBody?: ScheduleEventFullDaysRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-event-full-days-remove',
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
     * Use case for updating a full day block in the schedule.
     * Use case for updating a full day block in the schedule.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public scheduleEventFullDaysUpdate(
        requestBody?: ScheduleEventFullDaysUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-event-full-days-update',
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
