import { JournalSource } from "@jupiter/webapi-client";

export function journalSourceName(source: JournalSource) {
  switch (source) {
    case JournalSource.USER:
      return "User";
    case JournalSource.GENERATED:
      return "Generated";
  }
}

export function allowUserChanges(source: JournalSource) {
  // Keep synced with python:journal-source.py
  return source === JournalSource.USER;
}
