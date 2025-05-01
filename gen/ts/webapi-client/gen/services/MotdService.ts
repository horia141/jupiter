/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MOTDGetForTodayArgs } from '../models/MOTDGetForTodayArgs';
import type { MOTDGetForTodayResult } from '../models/MOTDGetForTodayResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class MotdService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Use case for getting a random Message of the Day.
     * Use case for getting a random Message of the Day.
     * @param requestBody The input data
     * @returns MOTDGetForTodayResult Successful response
     * @throws ApiError
     */
    public motdGetForToday(
        requestBody?: MOTDGetForTodayArgs,
    ): CancelablePromise<MOTDGetForTodayResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/motd-get-for-today',
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
