import { Eisen } from "webapi-client";
import { eisenName } from "~/logic/domain/eisen";
import { SlimChip } from "./infra/chips";

interface Props {
  eisen: Eisen;
}

export function EisenTag(props: Props) {
  const tagName = eisenName(props.eisen);
  const tagClass = eisenToClass(props.eisen);
  return <SlimChip label={tagName} color={tagClass} />;
}

function eisenToClass(eisen: Eisen) {
  switch (eisen) {
    case Eisen.REGULAR:
      return "default";
    case Eisen.IMPORTANT:
      return "success";
    case Eisen.URGENT:
      return "warning";
    case Eisen.IMPORTANT_AND_URGENT:
      return "error";
  }
}
