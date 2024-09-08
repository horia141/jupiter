/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FullDaysBlockLoadArgs } from '../models/FullDaysBlockLoadArgs';
import type { FullDaysBlockLoadResult } from '../models/FullDaysBlockLoadResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class FullDaysBlockService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Load a full day block and associated data.
     * Load a full day block and associated data.
     * @param requestBody The input data
     * @returns FullDaysBlockLoadResult Successful response
     * @throws ApiError
     */
    public fullDaysBlockLoad(
        requestBody?: FullDaysBlockLoadArgs,
    ): CancelablePromise<FullDaysBlockLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/full-days-block-load',
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
