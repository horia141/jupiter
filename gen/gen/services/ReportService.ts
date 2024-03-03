/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ReportArgs } from '../models/ReportArgs';
import type { ReportResult } from '../models/ReportResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class ReportService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

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

}
