/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TimeEventInDayBlockArchiveArgs } from '../models/TimeEventInDayBlockArchiveArgs';
import type { TimeEventInDayBlockCreateForInboxTaskArgs } from '../models/TimeEventInDayBlockCreateForInboxTaskArgs';
import type { TimeEventInDayBlockCreateForInboxTaskResult } from '../models/TimeEventInDayBlockCreateForInboxTaskResult';
import type { TimeEventInDayBlockLoadArgs } from '../models/TimeEventInDayBlockLoadArgs';
import type { TimeEventInDayBlockLoadResult } from '../models/TimeEventInDayBlockLoadResult';
import type { TimeEventInDayBlockRemoveArgs } from '../models/TimeEventInDayBlockRemoveArgs';
import type { TimeEventInDayBlockUpdateArgs } from '../models/TimeEventInDayBlockUpdateArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class InDayBlockService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Use case for archiving the in day event.
     * Use case for archiving the in day event.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public timeEventInDayBlockArchive(
        requestBody?: TimeEventInDayBlockArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-event-in-day-block-archive',
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
     * Use case for creating a time event associated with an inbox task.
     * Use case for creating a time event associated with an inbox task.
     * @param requestBody The input data
     * @returns TimeEventInDayBlockCreateForInboxTaskResult Successful response
     * @throws ApiError
     */
    public timeEventInDayBlockCreateForInboxTask(
        requestBody?: TimeEventInDayBlockCreateForInboxTaskArgs,
    ): CancelablePromise<TimeEventInDayBlockCreateForInboxTaskResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-event-in-day-block-create-for-inbox-task',
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
     * Load a in day block and associated data.
     * Load a in day block and associated data.
     * @param requestBody The input data
     * @returns TimeEventInDayBlockLoadResult Successful response
     * @throws ApiError
     */
    public timeEventInDayBlockLoad(
        requestBody?: TimeEventInDayBlockLoadArgs,
    ): CancelablePromise<TimeEventInDayBlockLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-event-in-day-block-load',
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
     * Use case for removing the in day event.
     * Use case for removing the in day event.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public timeEventInDayBlockRemove(
        requestBody?: TimeEventInDayBlockRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-event-in-day-block-remove',
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
     * Use case for updating a time event in day.
     * Use case for updating a time event in day.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public timeEventInDayBlockUpdate(
        requestBody?: TimeEventInDayBlockUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/time-event-in-day-block-update',
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
