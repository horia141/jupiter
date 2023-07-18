/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * The level of control allowed for a particular feature.
 */
export enum FeatureControl {
    ALWAYS_ON = 'always-on',
    ALWAYS_OFF_TECH = 'always-off-tech',
    ALWAYS_OFF_HOSTING = 'always-off-hosting',
    USER = 'user',
}
