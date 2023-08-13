import type { ADate } from "jupiter-gen";
import { aDateToDate } from "~/logic/domain/adate";
import { SlimChip } from "./infra/chips";

interface Props {
  label: string;
  date: ADate;
  color?:
    | "default"
    | "primary"
    | "secondary"
    | "error"
    | "info"
    | "success"
    | "warning";
}

export function ADateTag(props: Props) {
  return (
    <SlimChip
      label={`${props.label} ${aDateToDate(props.date)
        .setLocale("en-gb")
        .toLocaleString()}`}
      color={props.color ?? "info"}
    />
  );
}
