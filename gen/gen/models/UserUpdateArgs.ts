/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Timezone } from './Timezone';
import type { UserName } from './UserName';
export type UserUpdateArgs = {
    name: {
        should_change: boolean;
        value?: UserName;
    };
    timezone: {
        should_change: boolean;
        value?: Timezone;
    };
};

