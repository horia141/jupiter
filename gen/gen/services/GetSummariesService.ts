/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GetSummariesArgs } from '../models/GetSummariesArgs';
import type { GetSummariesResult } from '../models/GetSummariesResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class GetSummariesService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Get Summaries
     * Get summaries about entities.
     * @param requestBody
     * @returns GetSummariesResult Successful Response
     * @throws ApiError
     */
    public getSummaries(
        requestBody: GetSummariesArgs,
    ): CancelablePromise<GetSummariesResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/get-summaries',
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
