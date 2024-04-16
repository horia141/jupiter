/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Doc } from './Doc';
import type { Note } from './Note';

/**
 * DocCreate result.
 */
export type DocCreateResult = {
    new_doc: Doc;
    new_note: Note;
};

