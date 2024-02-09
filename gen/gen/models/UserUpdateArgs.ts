/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EntityName } from './EntityName';
import type { Timezone } from './Timezone';
export type UserUpdateArgs = {
    name: {
        should_change: boolean;
        value?: EntityName;
    };
    timezone: {
        should_change: boolean;
        value?: Timezone;
    };
};

