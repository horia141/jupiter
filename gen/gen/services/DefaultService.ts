/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_old_skool_login } from '../models/Body_old_skool_login';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class DefaultService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Old Skool Login
     * Login via OAuth2 password flow and return an auth token.
     * @param formData
     * @returns string Successful Response
     * @throws ApiError
     */
    public oldSkoolLogin(
        formData: Body_old_skool_login,
    ): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/old-skool-login',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
