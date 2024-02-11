/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChangePasswordArgs } from '../models/ChangePasswordArgs';
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
        requestBody?: ChangePasswordArgs,
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
        requestBody?: ChangePasswordArgs,
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public bigPlanCreate(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public bigPlanFind(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public bigPlanLoad(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
        requestBody?: ChangePasswordArgs,
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public bigPlanUpdate(
        requestBody?: ChangePasswordArgs,
    ): CancelablePromise<any> {
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
