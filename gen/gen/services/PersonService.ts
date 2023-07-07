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
import type { PersonUpdateArgs } from '../models/PersonUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class PersonService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Create Person
     * Create a person.
     * @param requestBody
     * @returns PersonCreateResult Successful Response
     * @throws ApiError
     */
    public createPerson(
        requestBody: PersonCreateArgs,
    ): CancelablePromise<PersonCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person/create',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Archive Person
     * Archive a person.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archivePerson(
        requestBody: PersonArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person/archive',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Person
     * Update a person.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updatePerson(
        requestBody: PersonUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person/update',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Load Person Settings
     * Change the catch up project for persons.
     * @param requestBody
     * @returns PersonLoadSettingsResult Successful Response
     * @throws ApiError
     */
    public loadPersonSettings(
        requestBody: PersonLoadSettingsArgs,
    ): CancelablePromise<PersonLoadSettingsResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person/load-settings',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Change Catch Up Project
     * Change the catch up project for persons.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateChangeCatchUpProject(
        requestBody: PersonChangeCatchUpProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person/change-catch-up-project',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Load Person
     * Load a person, filtering by id.
     * @param requestBody
     * @returns PersonLoadResult Successful Response
     * @throws ApiError
     */
    public loadPerson(
        requestBody: PersonLoadArgs,
    ): CancelablePromise<PersonLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person/load',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Find Person
     * Find a person, filtering by id.
     * @param requestBody
     * @returns PersonFindResult Successful Response
     * @throws ApiError
     */
    public findPerson(
        requestBody: PersonFindArgs,
    ): CancelablePromise<PersonFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/person/find',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
