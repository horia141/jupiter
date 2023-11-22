/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GCDoArgs } from '../models/GCDoArgs';
import type { GCLoadRunsArgs } from '../models/GCLoadRunsArgs';
import type { GCLoadRunsResult } from '../models/GCLoadRunsResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class GcService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Gc Do
     * Perform a garbage collect.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public gcDo(
        requestBody: GCDoArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/gc/do',
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
     * Gc Load Runs
     * Load history of GC runs.
     * @param requestBody
     * @returns GCLoadRunsResult Successful Response
     * @throws ApiError
     */
    public gcLoadRuns(
        requestBody: GCLoadRunsArgs,
    ): CancelablePromise<GCLoadRunsResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/gc/load-runs',
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
