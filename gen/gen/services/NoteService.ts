/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NoteArchiveArgs } from '../models/NoteArchiveArgs';
import type { NoteChangeParentArgs } from '../models/NoteChangeParentArgs';
import type { NoteCreateArgs } from '../models/NoteCreateArgs';
import type { NoteCreateResult } from '../models/NoteCreateResult';
import type { NoteFindArgs } from '../models/NoteFindArgs';
import type { NoteFindResult } from '../models/NoteFindResult';
import type { NoteLoadArgs } from '../models/NoteLoadArgs';
import type { NoteLoadResult } from '../models/NoteLoadResult';
import type { NoteUpdateArgs } from '../models/NoteUpdateArgs';

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
            url: '/note/create',
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
            url: '/note/archive',
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
            url: '/note/update',
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
     * Change Note Parent
     * Change the parent for a note.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public changeNoteParent(
        requestBody: NoteChangeParentArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/note/change-parent',
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
     * Load Note
     * Load a note.
     * @param requestBody
     * @returns NoteLoadResult Successful Response
     * @throws ApiError
     */
    public loadNote(
        requestBody: NoteLoadArgs,
    ): CancelablePromise<NoteLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/note/load',
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
     * Find Note
     * Find all notes, filtering by id.
     * @param requestBody
     * @returns NoteFindResult Successful Response
     * @throws ApiError
     */
    public findNote(
        requestBody: NoteFindArgs,
    ): CancelablePromise<NoteFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/note/find',
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
