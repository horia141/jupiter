/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HomeConfigLoadArgs } from '../models/HomeConfigLoadArgs';
import type { HomeConfigLoadResult } from '../models/HomeConfigLoadResult';
import type { HomeConfigUpdateArgs } from '../models/HomeConfigUpdateArgs';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class HomeService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The use case for loading the home config.
     * The use case for loading the home config.
     * @param requestBody The input data
     * @returns HomeConfigLoadResult Successful response
     * @throws ApiError
     */
    public homeConfigLoad(
        requestBody?: HomeConfigLoadArgs,
    ): CancelablePromise<HomeConfigLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/home-config-load',
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
     * The use case for updating the home config.
     * The use case for updating the home config.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public homeConfigUpdate(
        requestBody?: HomeConfigUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/home-config-update',
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
