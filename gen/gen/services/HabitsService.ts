/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { HabitArchiveArgs } from '../models/HabitArchiveArgs';
import type { HabitChangeProjectArgs } from '../models/HabitChangeProjectArgs';
import type { HabitCreateArgs } from '../models/HabitCreateArgs';
import type { HabitFindArgs } from '../models/HabitFindArgs';
import type { HabitLoadArgs } from '../models/HabitLoadArgs';
import type { HabitRemoveArgs } from '../models/HabitRemoveArgs';
import type { HabitSuspendArgs } from '../models/HabitSuspendArgs';
import type { HabitUnsuspendArgs } from '../models/HabitUnsuspendArgs';
import type { HabitUpdateArgs } from '../models/HabitUpdateArgs';
import type { ModelHabitCreateResult } from '../models/ModelHabitCreateResult';
import type { ModelHabitFindResult } from '../models/ModelHabitFindResult';
import type { ModelHabitLoadResult } from '../models/ModelHabitLoadResult';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class HabitsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * The command for archiving a habit.
     * The command for archiving a habit.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public habitArchive(
        requestBody: HabitArchiveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit-archive',
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
     * The command for changing the project of a habit.
     * The command for changing the project of a habit.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public habitChangeProject(
        requestBody: HabitChangeProjectArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit-change-project',
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
     * The command for creating a habit.
     * The command for creating a habit.
     * @param requestBody
     * @returns ModelHabitCreateResult Successful Response
     * @throws ApiError
     */
    public habitCreate(
        requestBody: HabitCreateArgs,
    ): CancelablePromise<ModelHabitCreateResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit-create',
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
     * The command for finding a habit.
     * The command for finding a habit.
     * @param requestBody
     * @returns ModelHabitFindResult Successful Response
     * @throws ApiError
     */
    public habitFind(
        requestBody: HabitFindArgs,
    ): CancelablePromise<ModelHabitFindResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit-find',
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
     * Use case for loading a particular habit.
     * Use case for loading a particular habit.
     * @param requestBody
     * @returns ModelHabitLoadResult Successful Response
     * @throws ApiError
     */
    public habitLoad(
        requestBody: HabitLoadArgs,
    ): CancelablePromise<ModelHabitLoadResult> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit-load',
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
     * The command for removing a habit.
     * The command for removing a habit.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public habitRemove(
        requestBody: HabitRemoveArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit-remove',
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
     * The command for suspending a habit.
     * The command for suspending a habit.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public habitSuspend(
        requestBody: HabitSuspendArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit-suspend',
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
     * The command for unsuspending a habit.
     * The command for unsuspending a habit.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public habitUnsuspend(
        requestBody: HabitUnsuspendArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit-unsuspend',
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
     * The command for updating a habit.
     * The command for updating a habit.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public habitUpdate(
        requestBody: HabitUpdateArgs,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/habit-update',
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
