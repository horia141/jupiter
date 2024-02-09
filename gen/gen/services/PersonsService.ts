/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PersonArchiveArgs } from '../models/PersonArchiveArgs';
import type { PersonChangeCatchUpProjectArgs } from '../models/PersonChangeCatchUpProjectArgs';
import type { PersonCreateArgs } from '../models/PersonCreateArgs';
import type { PersonCreateResult } from '../models/PersonCreateResult';
import type { PersonFindArgs } from '../models/PersonFindArgs';
import type { PersonFindResult } from '../models/PersonFindResult';
import type { PersonLoadArgs } from '../models/PersonLoadArgs';
import type { PersonLoadResult } from '../models/PersonLoadResult';
import type { PersonLoadSettingsArgs } from '../models/PersonLoadSettingsArgs';
import type { PersonLoadSettingsResult } from '../models/PersonLoadSettingsResult';
import type { PersonRemoveArgs } from '../models/PersonRemoveArgs';
import type { PersonUpdateArgs } from '../models/PersonUpdateArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class PersonsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a person.
     * The command for archiving a person.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public personArchive(
        requestBody: PersonArchiveArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person-archive',
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
     * The command for updating the catch up project for persons.
     * The command for updating the catch up project for persons.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public personChangeCatchUpProject(
        requestBody: PersonChangeCatchUpProjectArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person-change-catch-up-project',
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
     * The command for creating a person.
     * The command for creating a person.
     * @param requestBody
     * @returns PersonCreateResult Successful Response
     * @throws ApiError
     */
    public personCreate(
        requestBody: PersonCreateArgs,
    ): CancelablePromise<PersonCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person-create',
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
     * The command for finding the persons.
     * The command for finding the persons.
     * @param requestBody
     * @returns PersonFindResult Successful Response
     * @throws ApiError
     */
    public personFind(
        requestBody: PersonFindArgs,
    ): CancelablePromise<PersonFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person-find',
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
     * Use case for loading a person.
     * Use case for loading a person.
     * @param requestBody
     * @returns PersonLoadResult Successful Response
     * @throws ApiError
     */
    public personLoad(
        requestBody: PersonLoadArgs,
    ): CancelablePromise<PersonLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person-load',
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
     * The command for loading the settings around persons.
     * The command for loading the settings around persons.
     * @param requestBody
     * @returns PersonLoadSettingsResult Successful Response
     * @throws ApiError
     */
    public personLoadSettings(
        requestBody: PersonLoadSettingsArgs,
    ): CancelablePromise<PersonLoadSettingsResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person-load-settings',
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
     * The command for removing a person.
     * The command for removing a person.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public personRemove(
        requestBody: PersonRemoveArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person-remove',
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
     * The command for updating a person.
     * The command for updating a person.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public personUpdate(
        requestBody: PersonUpdateArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person-update',
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
