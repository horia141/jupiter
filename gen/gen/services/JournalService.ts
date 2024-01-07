/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { JournalArchiveArgs } from '../models/JournalArchiveArgs';
import type { JournalChangeTimeConfigArgs } from '../models/JournalChangeTimeConfigArgs';
import type { JournalCreateArgs } from '../models/JournalCreateArgs';
import type { JournalCreateResult } from '../models/JournalCreateResult';
import type { JournalFindArgs } from '../models/JournalFindArgs';
import type { JournalFindResult } from '../models/JournalFindResult';
import type { JournalLoadArgs } from '../models/JournalLoadArgs';
import type { JournalLoadResult } from '../models/JournalLoadResult';
import type { JournalUpdateReportArgs } from '../models/JournalUpdateReportArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class JournalService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Create Journal
     * Create a journal.
     * @param requestBody
     * @returns JournalCreateResult Successful Response
     * @throws ApiError
     */
    public createJournal(
        requestBody: JournalCreateArgs,
    ): CancelablePromise<JournalCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal/create',
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
     * Archive Journal
     * Archive a journal.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveJournal(
        requestBody: JournalArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal/archive',
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
     * Change Time Config For Journal
     * Change time config for a journal.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public changeTimeConfigForJournal(
        requestBody: JournalChangeTimeConfigArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal/change-time-config',
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
     * Update Report For Jorunal
     * Change time config for a journal.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateReportForJorunal(
        requestBody: JournalUpdateReportArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal/update-report',
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
     * Find Journal
     * Find all journals, filtering by id.
     * @param requestBody
     * @returns JournalFindResult Successful Response
     * @throws ApiError
     */
    public findJournal(
        requestBody: JournalFindArgs,
    ): CancelablePromise<JournalFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal/find',
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
     * Load Journal
     * Load a journal.
     * @param requestBody
     * @returns JournalLoadResult Successful Response
     * @throws ApiError
     */
    public loadJournal(
        requestBody: JournalLoadArgs,
    ): CancelablePromise<JournalLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal/load',
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
