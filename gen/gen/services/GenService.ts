/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GenArgs } from '../models/GenArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class GenService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Gen
     * Generate inbox tasks.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public gen(
        requestBody: GenArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/gen',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
