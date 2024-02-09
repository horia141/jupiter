/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LoadProgressReporterTokenArgs } from '../models/LoadProgressReporterTokenArgs';
import type { ModelLoadProgressReporterTokenResult } from '../models/ModelLoadProgressReporterTokenResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class LoadProgressReporterTokenService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The use case for retrieving summaries about entities.
     * The use case for retrieving summaries about entities.
     * @param requestBody
     * @returns ModelLoadProgressReporterTokenResult Successful Response
     * @throws ApiError
     */
    public loadProgressReporterToken(
        requestBody: LoadProgressReporterTokenArgs,
    ): CancelablePromise<ModelLoadProgressReporterTokenResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/load-progress-reporter-token',
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
