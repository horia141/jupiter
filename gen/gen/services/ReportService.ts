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
     * Report
     * Report.
     * @param requestBody
     * @returns ReportResult Successful Response
     * @throws ApiError
     */
    public report(
        requestBody: ReportArgs,
    ): CancelablePromise<ReportResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/report',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                404: `Workspace Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
