/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NoteArchiveArgs } from '../models/NoteArchiveArgs';
import type { NoteCreateArgs } from '../models/NoteCreateArgs';
import type { NoteCreateResult } from '../models/NoteCreateResult';
import type { NoteUpdateArgs } from '../models/NoteUpdateArgs';
import type { x } from '../models/x';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class NoteService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Create Note
     * Create a note.
     * @param requestBody
     * @returns NoteCreateResult Successful Response
     * @throws ApiError
     */
    public createNote(
        requestBody: NoteCreateArgs,
    ): CancelablePromise<NoteCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/core/note/create',
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
     * Archive Note
     * Archive a note.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveNote(
        requestBody: NoteArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/core/note/archive',
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
     * Update Note
     * Update a note.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateNote(
        requestBody: NoteUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/core/note/update',
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
     * Do X
     * Update a note.
     * @param requestBody
     * @returns x Successful Response
     * @throws ApiError
     */
    public doX(
        requestBody: x,
    ): CancelablePromise<x> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/x',
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
