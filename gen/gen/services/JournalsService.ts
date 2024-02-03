/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { JournalArchiveArgs } from '../models/JournalArchiveArgs';
import type { JournalChangePeriodsArgs } from '../models/JournalChangePeriodsArgs';
import type { JournalChangeTimeConfigArgs } from '../models/JournalChangeTimeConfigArgs';
import type { JournalCreateArgs } from '../models/JournalCreateArgs';
import type { JournalCreateResult } from '../models/JournalCreateResult';
import type { JournalFindArgs } from '../models/JournalFindArgs';
import type { JournalFindResult } from '../models/JournalFindResult';
import type { JournalLoadArgs } from '../models/JournalLoadArgs';
import type { JournalLoadResult } from '../models/JournalLoadResult';
import type { JournalLoadSettingsArgs } from '../models/JournalLoadSettingsArgs';
import type { JournalLoadSettingsResult } from '../models/JournalLoadSettingsResult';
import type { JournalremoveArgs } from '../models/JournalremoveArgs';
import type { JournalUpdateReportArgs } from '../models/JournalUpdateReportArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class JournalsService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Use case for archiving a journal.
     * Use case for archiving a journal.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public journalArchive(
        requestBody: JournalArchiveArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal-archive',
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
     * THe use case for changing periods for journals.
     * THe use case for changing periods for journals.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public journalChangePeriods(
        requestBody: JournalChangePeriodsArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal-change-periods',
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
     * Command for updating the time configuration of a journal.
     * Command for updating the time configuration of a journal.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public journalChangeTimeConfig(
        requestBody: JournalChangeTimeConfigArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal-change-time-config',
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
     * Use case for creating a journal.
     * Use case for creating a journal.
     * @param requestBody
     * @returns JournalCreateResult Successful Response
     * @throws ApiError
     */
    public journalCreate(
        requestBody: JournalCreateArgs,
    ): CancelablePromise<JournalCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal-create',
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
     * The command for finding journals.
     * The command for finding journals.
     * @param requestBody
     * @returns JournalFindResult Successful Response
     * @throws ApiError
     */
    public journalFind(
        requestBody: JournalFindArgs,
    ): CancelablePromise<JournalFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal-find',
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
     * The command for loading details about a journal.
     * The command for loading details about a journal.
     * @param requestBody
     * @returns JournalLoadResult Successful Response
     * @throws ApiError
     */
    public journalLoad(
        requestBody: JournalLoadArgs,
    ): CancelablePromise<JournalLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal-load',
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
     * The command for loading the settings around journals.
     * The command for loading the settings around journals.
     * @param requestBody
     * @returns JournalLoadSettingsResult Successful Response
     * @throws ApiError
     */
    public journalLoadSettings(
        requestBody: JournalLoadSettingsArgs,
    ): CancelablePromise<JournalLoadSettingsResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal-load-settings',
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
     * Use case for removing a journal.
     * Use case for removing a journal.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public journalRemove(
        requestBody: JournalremoveArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal-remove',
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
     * Use case for updating a journal entry.
     * Use case for updating a journal entry.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public journalUpdateReport(
        requestBody: JournalUpdateReportArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/journal-update-report',
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
