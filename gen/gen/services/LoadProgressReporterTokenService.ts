/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LoadProgressReporterTokenArgs } from '../models/LoadProgressReporterTokenArgs';
import type { LoadProgressReporterTokenResult } from '../models/LoadProgressReporterTokenResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class LoadProgressReporterTokenService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Load Progress Reporter Token
     * Load a temporary access token useful for reading progress reporter updates.
     * @param requestBody
     * @returns LoadProgressReporterTokenResult Successful Response
     * @throws ApiError
     */
    public loadProgressReporterToken(
        requestBody: LoadProgressReporterTokenArgs,
    ): CancelablePromise<LoadProgressReporterTokenResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/load-progress-reporter-token',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
