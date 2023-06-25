/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { InitArgs } from '../models/InitArgs';
import type { InitResult } from '../models/InitResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class InitService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Init
     * Initialise a new workspace.
     * @param requestBody
     * @returns InitResult Successful Response
     * @throws ApiError
     */
    public init(
        requestBody: InitArgs,
    ): CancelablePromise<InitResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/init',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
