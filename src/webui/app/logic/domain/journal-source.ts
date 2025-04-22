import { JournalSource } from "@jupiter/webapi-client";

export function journalSourceName(source: JournalSource) {
  switch (source) {
    case JournalSource.USER:
      return "User";
    case JournalSource.GENERATED:
      return "Generated";
  }
}
