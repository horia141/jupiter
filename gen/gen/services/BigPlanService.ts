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
import type { BigPlanUpdateArgs } from '../models/BigPlanUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class BigPlanService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Create Big Plan
     * Create a big plan.
     * @param requestBody
     * @returns BigPlanCreateResult Successful Response
     * @throws ApiError
     */
    public createBigPlan(
        requestBody: BigPlanCreateArgs,
    ): CancelablePromise<BigPlanCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan/create',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Archive Big Plan
     * Archive a big plan.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveBigPlan(
        requestBody: BigPlanArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan/archive',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Big Plan
     * Update a big plan.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateBigPlan(
        requestBody: BigPlanUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan/update',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Change Big Plan Project
     * Change the project for a big plan.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public changeBigPlanProject(
        requestBody: BigPlanChangeProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan/change-project',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Load Big Plan
     * Load a big plan.
     * @param requestBody
     * @returns BigPlanLoadResult Successful Response
     * @throws ApiError
     */
    public loadBigPlan(
        requestBody: BigPlanLoadArgs,
    ): CancelablePromise<BigPlanLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan/load',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Find Big Plan
     * Find all big plans, filtering by id.
     * @param requestBody
     * @returns BigPlanFindResult Successful Response
     * @throws ApiError
     */
    public findBigPlan(
        requestBody: BigPlanFindArgs,
    ): CancelablePromise<BigPlanFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan/find',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
