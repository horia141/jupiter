/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BigPlanMilestoneArchiveArgs } from '../models/BigPlanMilestoneArchiveArgs';
import type { BigPlanMilestoneCreateArgs } from '../models/BigPlanMilestoneCreateArgs';
import type { BigPlanMilestoneCreateResult } from '../models/BigPlanMilestoneCreateResult';
import type { BigPlanMilestoneLoadArgs } from '../models/BigPlanMilestoneLoadArgs';
import type { BigPlanMilestoneLoadResult } from '../models/BigPlanMilestoneLoadResult';
import type { BigPlanMilestoneRemoveArgs } from '../models/BigPlanMilestoneRemoveArgs';
import type { BigPlanMilestoneUpdateArgs } from '../models/BigPlanMilestoneUpdateArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class MilestonesService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a big plan milestone.
     * The command for archiving a big plan milestone.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public bigPlanMilestoneArchive(
        requestBody?: BigPlanMilestoneArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan-milestone-archive',
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
     * The command for creating a big plan milestone.
     * The command for creating a big plan milestone.
     * @param requestBody The input data
     * @returns BigPlanMilestoneCreateResult Successful response
     * @throws ApiError
     */
    public bigPlanMilestoneCreate(
        requestBody?: BigPlanMilestoneCreateArgs,
    ): CancelablePromise<BigPlanMilestoneCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan-milestone-create',
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
     * The use case for loading a particular big plan milestone.
     * The use case for loading a particular big plan milestone.
     * @param requestBody The input data
     * @returns BigPlanMilestoneLoadResult Successful response
     * @throws ApiError
     */
    public bigPlanMilestoneLoad(
        requestBody?: BigPlanMilestoneLoadArgs,
    ): CancelablePromise<BigPlanMilestoneLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan-milestone-load',
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
     * The command for removing a big plan milestone.
     * The command for removing a big plan milestone.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public bigPlanMilestoneRemove(
        requestBody?: BigPlanMilestoneRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan-milestone-remove',
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
     * The command for updating a big plan milestone.
     * The command for updating a big plan milestone.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public bigPlanMilestoneUpdate(
        requestBody?: BigPlanMilestoneUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/big-plan-milestone-update',
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
