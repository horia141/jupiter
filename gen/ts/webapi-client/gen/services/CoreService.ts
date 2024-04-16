/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NoteArchiveArgs } from '../models/NoteArchiveArgs';
import type { NoteCreateArgs } from '../models/NoteCreateArgs';
import type { NoteCreateResult } from '../models/NoteCreateResult';
import type { NoteRemoveArgs } from '../models/NoteRemoveArgs';
import type { NoteUpdateArgs } from '../models/NoteUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class CoreService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Use case for archiving a note.
     * Use case for archiving a note.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public noteArchive(
        requestBody?: NoteArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/note-archive',
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
     * Use case for creating a note.
     * Use case for creating a note.
     * @param requestBody The input data
     * @returns NoteCreateResult Successful response
     * @throws ApiError
     */
    public noteCreate(
        requestBody?: NoteCreateArgs,
    ): CancelablePromise<NoteCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/note-create',
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
     * The command for removing a note.
     * The command for removing a note.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public noteRemove(
        requestBody?: NoteRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/note-remove',
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
     * Update a note use case.
     * Update a note use case.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public noteUpdate(
        requestBody?: NoteUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/note-update',
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
