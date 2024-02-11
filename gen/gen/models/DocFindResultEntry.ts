/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Doc } from './Doc';
import type { Note } from './Note';
/**
 * A single entry in the load all docs response.
 */
export type DocFindResultEntry = {
    doc: Doc;
    note?: Note;
    subdocs?: Array<Doc>;
};

