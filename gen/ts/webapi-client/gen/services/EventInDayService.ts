/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ScheduleEventInDayArchiveArgs } from '../models/ScheduleEventInDayArchiveArgs';
import type { ScheduleEventInDayChangeScheduleStreamArgs } from '../models/ScheduleEventInDayChangeScheduleStreamArgs';
import type { ScheduleEventInDayCreateArgs } from '../models/ScheduleEventInDayCreateArgs';
import type { ScheduleEventInDayCreateResult } from '../models/ScheduleEventInDayCreateResult';
import type { ScheduleEventInDayLoadArgs } from '../models/ScheduleEventInDayLoadArgs';
import type { ScheduleEventInDayLoadResult } from '../models/ScheduleEventInDayLoadResult';
import type { ScheduleEventInDayRemoveArgs } from '../models/ScheduleEventInDayRemoveArgs';
import type { ScheduleEventInDayUpdateArgs } from '../models/ScheduleEventInDayUpdateArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class EventInDayService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Use case for archiving a schedule in day event.
     * Use case for archiving a schedule in day event.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public scheduleEventInDayArchive(
        requestBody?: ScheduleEventInDayArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-event-in-day-archive',
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
    public scheduleEventInDayChangeScheduleStream(
        requestBody?: ScheduleEventInDayChangeScheduleStreamArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-event-in-day-change-schedule-stream',
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
     * Use case for creating a schedule in day event.
     * Use case for creating a schedule in day event.
     * @param requestBody The input data
     * @returns ScheduleEventInDayCreateResult Successful response
     * @throws ApiError
     */
    public scheduleEventInDayCreate(
        requestBody?: ScheduleEventInDayCreateArgs,
    ): CancelablePromise<ScheduleEventInDayCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-event-in-day-create',
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
     * Use case for loading a schedule in day event.
     * Use case for loading a schedule in day event.
     * @param requestBody The input data
     * @returns ScheduleEventInDayLoadResult Successful response
     * @throws ApiError
     */
    public scheduleEventInDayLoad(
        requestBody?: ScheduleEventInDayLoadArgs,
    ): CancelablePromise<ScheduleEventInDayLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-event-in-day-load',
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
     * Use case for removing a schedule in day event.
     * Use case for removing a schedule in day event.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public scheduleEventInDayRemove(
        requestBody?: ScheduleEventInDayRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-event-in-day-remove',
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
     * Use case for updating a schedule in day event.
     * Use case for updating a schedule in day event.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public scheduleEventInDayUpdate(
        requestBody?: ScheduleEventInDayUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/schedule-event-in-day-update',
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
