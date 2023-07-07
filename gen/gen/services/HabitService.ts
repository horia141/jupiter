/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HabitArchiveArgs } from '../models/HabitArchiveArgs';
import type { HabitChangeProjectArgs } from '../models/HabitChangeProjectArgs';
import type { HabitCreateArgs } from '../models/HabitCreateArgs';
import type { HabitCreateResult } from '../models/HabitCreateResult';
import type { HabitFindArgs } from '../models/HabitFindArgs';
import type { HabitFindResult } from '../models/HabitFindResult';
import type { HabitLoadArgs } from '../models/HabitLoadArgs';
import type { HabitLoadResult } from '../models/HabitLoadResult';
import type { HabitSuspendArgs } from '../models/HabitSuspendArgs';
import type { HabitUnsuspendArgs } from '../models/HabitUnsuspendArgs';
import type { HabitUpdateArgs } from '../models/HabitUpdateArgs';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class HabitService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Create Habit
     * Create a habit.
     * @param requestBody
     * @returns HabitCreateResult Successful Response
     * @throws ApiError
     */
    public createHabit(
        requestBody: HabitCreateArgs,
    ): CancelablePromise<HabitCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit/create',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Archive Habit
     * Archive a habit.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public archiveHabit(
        requestBody: HabitArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit/archive',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Habit
     * Update a habit.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public updateHabit(
        requestBody: HabitUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit/update',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Change Habit Project
     * Change the project for a habit.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public changeHabitProject(
        requestBody: HabitChangeProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit/change-project',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Suspend Habit
     * Suspend a habit.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public suspendHabit(
        requestBody: HabitSuspendArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit/suspend',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Unsuspend Habit
     * Unsuspend a habit.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public unsuspendHabit(
        requestBody: HabitUnsuspendArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit/unsuspend',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Load Habit
     * Load a habit.
     * @param requestBody
     * @returns HabitLoadResult Successful Response
     * @throws ApiError
     */
    public loadHabit(
        requestBody: HabitLoadArgs,
    ): CancelablePromise<HabitLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit/load',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Find Habit
     * Find all habits, filtering by id..
     * @param requestBody
     * @returns HabitFindResult Successful Response
     * @throws ApiError
     */
    public findHabit(
        requestBody: HabitFindArgs,
    ): CancelablePromise<HabitFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit/find',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                410: `Workspace Or User Not Found`,
                422: `Validation Error`,
            },
        });
    }

}
