/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CloseAccountArgs } from '../models/CloseAccountArgs';
import type { InitArgs } from '../models/InitArgs';
import type { InitResult } from '../models/InitResult';
import type { ReportArgs } from '../models/ReportArgs';
import type { ReportResult } from '../models/ReportResult';
import type { SearchArgs } from '../models/SearchArgs';
import type { SearchResult } from '../models/SearchResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class ApplicationService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Close account use case.
     * Close account use case.
     * @param requestBody The input data
     * @returns any Successful response / Empty body
     * @throws ApiError
     */
    public closeAccount(
        requestBody?: CloseAccountArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/close-account',
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
     * UseCase for initialising the workspace.
     * UseCase for initialising the workspace.
     * @param requestBody The input data
     * @returns InitResult Successful response
     * @throws ApiError
     */
    public init(
        requestBody?: InitArgs,
    ): CancelablePromise<InitResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/init',
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
     * The command for reporting on progress.
     * The command for reporting on progress.
     * @param requestBody The input data
     * @returns ReportResult Successful response
     * @throws ApiError
     */
    public report(
        requestBody?: ReportArgs,
    ): CancelablePromise<ReportResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/report',
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
     * Use case for free form searching through jupiter.
     * Use case for free form searching through jupiter.
     * @param requestBody The input data
     * @returns SearchResult Successful response
     * @throws ApiError
     */
    public search(
        requestBody?: SearchArgs,
    ): CancelablePromise<SearchResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/search',
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
