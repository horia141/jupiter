/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BigPlanArchiveArgs } from '../models/BigPlanArchiveArgs';
import type { BigPlanChangeProjectArgs } from '../models/BigPlanChangeProjectArgs';
import type { BigPlanCreateArgs } from '../models/BigPlanCreateArgs';
import type { BigPlanCreateResult } from '../models/BigPlanCreateResult';
import type { BigPlanFindArgs } from '../models/BigPlanFindArgs';
import type { BigPlanFindResult } from '../models/BigPlanFindResult';
import type { BigPlanLoadArgs } from '../models/BigPlanLoadArgs';
import type { BigPlanLoadResult } from '../models/BigPlanLoadResult';
import type { BigPlanRemoveArgs } from '../models/BigPlanRemoveArgs';
import type { BigPlanUpdateArgs } from '../models/BigPlanUpdateArgs';
import type { BigPlanUpdateResult } from '../models/BigPlanUpdateResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class BigPlansService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a big plan.
     * The command for archiving a big plan.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public bigPlanArchive(
        requestBody: BigPlanArchiveArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan-archive',
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
     * The command for changing the project of a big plan.
     * The command for changing the project of a big plan.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public bigPlanChangeProject(
        requestBody: BigPlanChangeProjectArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan-change-project',
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
     * The command for creating a big plan.
     * The command for creating a big plan.
     * @param requestBody
     * @returns BigPlanCreateResult Successful Response
     * @throws ApiError
     */
    public bigPlanCreate(
        requestBody: BigPlanCreateArgs,
    ): CancelablePromise<BigPlanCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan-create',
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
     * The command for finding a big plan.
     * The command for finding a big plan.
     * @param requestBody
     * @returns BigPlanFindResult Successful Response
     * @throws ApiError
     */
    public bigPlanFind(
        requestBody: BigPlanFindArgs,
    ): CancelablePromise<BigPlanFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan-find',
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
     * The use case for loading a particular big plan.
     * The use case for loading a particular big plan.
     * @param requestBody
     * @returns BigPlanLoadResult Successful Response
     * @throws ApiError
     */
    public bigPlanLoad(
        requestBody: BigPlanLoadArgs,
    ): CancelablePromise<BigPlanLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan-load',
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
     * The command for removing a big plan.
     * The command for removing a big plan.
     * @param requestBody
     * @returns null Successful Response
     * @throws ApiError
     */
    public bigPlanRemove(
        requestBody: BigPlanRemoveArgs,
    ): CancelablePromise<null> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan-remove',
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
     * The command for updating a big plan.
     * The command for updating a big plan.
     * @param requestBody
     * @returns BigPlanUpdateResult Successful Response
     * @throws ApiError
     */
    public bigPlanUpdate(
        requestBody: BigPlanUpdateArgs,
    ): CancelablePromise<BigPlanUpdateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan-update',
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
