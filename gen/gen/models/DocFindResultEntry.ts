/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Doc } from './Doc';
import type { Note } from './Note';

export type DocFindResultEntry = {
    doc: Doc;
    note?: Note;
    subdocs?: Array<Doc>;
};

