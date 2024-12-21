/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CalendarLoadForDateAndPeriodArgs } from '../models/CalendarLoadForDateAndPeriodArgs';
import type { CalendarLoadForDateAndPeriodResult } from '../models/CalendarLoadForDateAndPeriodResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class CalendarService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Use case for loading all the calendar entities for a given date and period.
     * Use case for loading all the calendar entities for a given date and period.
     * @param requestBody The input data
     * @returns CalendarLoadForDateAndPeriodResult Successful response
     * @throws ApiError
     */
    public calendarLoadForDateAndPeriod(
        requestBody?: CalendarLoadForDateAndPeriodArgs,
    ): CancelablePromise<CalendarLoadForDateAndPeriodResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/calendar-load-for-date-and-period',
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
