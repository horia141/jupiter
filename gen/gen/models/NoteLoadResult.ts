/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Note } from './Note';

export type NoteLoadResult = {
    note: Note;
    subnotes: Array<Note>;
};
