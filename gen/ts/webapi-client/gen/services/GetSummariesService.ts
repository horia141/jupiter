/* generated using openapi-typescript-codegen -- do not edit */
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
     * The use case for retrieving summaries about entities.
     * The use case for retrieving summaries about entities.
     * @param requestBody The input data
     * @returns GetSummariesResult Successful response
     * @throws ApiError
     */
    public getSummaries(
        requestBody?: GetSummariesArgs,
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
