import { JournalSource } from "@jupiter/webapi-client";
import { journalSourceName } from "~/logic/domain/journal";

import { SlimChip } from "./infra/chips";

interface Props {
  source: JournalSource;
}

export function JournalSourceTag({ source }: Props) {
  const tagName = journalSourceName(source);
  const tagClass = sourceToClass(source);
  return <SlimChip label={tagName} color={tagClass} />;
}

function sourceToClass(source: JournalSource): "info" | "warning" {
  switch (source) {
    case JournalSource.USER:
      return "info";
    case JournalSource.RECURRING:
      return "warning";
  }
}
