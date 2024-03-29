/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Doc } from './Doc';
import type { Note } from './Note';

/**
 * DocLoad result.
 */
export type DocLoadResult = {
    doc: Doc;
    note: Note;
    subdocs: Array<Doc>;
};

