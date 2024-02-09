/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BigPlanArchiveArgs } from '../models/BigPlanArchiveArgs';
import type { BigPlanChangeProjectArgs } from '../models/BigPlanChangeProjectArgs';
import type { BigPlanCreateArgs } from '../models/BigPlanCreateArgs';
import type { BigPlanFindArgs } from '../models/BigPlanFindArgs';
import type { BigPlanLoadArgs } from '../models/BigPlanLoadArgs';
import type { BigPlanRemoveArgs } from '../models/BigPlanRemoveArgs';
import type { BigPlanUpdateArgs } from '../models/BigPlanUpdateArgs';
import type { ModelBigPlanCreateResult } from '../models/ModelBigPlanCreateResult';
import type { ModelBigPlanFindResult } from '../models/ModelBigPlanFindResult';
import type { ModelBigPlanLoadResult } from '../models/ModelBigPlanLoadResult';
import type { ModelBigPlanUpdateResult } from '../models/ModelBigPlanUpdateResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class BigPlansService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a big plan.
     * The command for archiving a big plan.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public bigPlanArchive(
        requestBody: BigPlanArchiveArgs,
    ): CancelablePromise<any> {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public bigPlanChangeProject(
        requestBody: BigPlanChangeProjectArgs,
    ): CancelablePromise<any> {
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
     * @returns ModelBigPlanCreateResult Successful Response
     * @throws ApiError
     */
    public bigPlanCreate(
        requestBody: BigPlanCreateArgs,
    ): CancelablePromise<ModelBigPlanCreateResult> {
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
     * @returns ModelBigPlanFindResult Successful Response
     * @throws ApiError
     */
    public bigPlanFind(
        requestBody: BigPlanFindArgs,
    ): CancelablePromise<ModelBigPlanFindResult> {
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
     * @returns ModelBigPlanLoadResult Successful Response
     * @throws ApiError
     */
    public bigPlanLoad(
        requestBody: BigPlanLoadArgs,
    ): CancelablePromise<ModelBigPlanLoadResult> {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public bigPlanRemove(
        requestBody: BigPlanRemoveArgs,
    ): CancelablePromise<any> {
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
     * @returns ModelBigPlanUpdateResult Successful Response
     * @throws ApiError
     */
    public bigPlanUpdate(
        requestBody: BigPlanUpdateArgs,
    ): CancelablePromise<ModelBigPlanUpdateResult> {
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
