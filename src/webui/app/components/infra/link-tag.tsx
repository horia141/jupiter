import { SlimChip } from "./chips";
import { EntityLink } from "./entity-card";

interface LinkTagProps {
  to: string;
  color:
    | "default"
    | "primary"
    | "secondary"
    | "error"
    | "info"
    | "success"
    | "warning";
  label: string;
}

export function LinkTag(props: LinkTagProps) {
  return (
    <EntityLink to={props.to}>
      <SlimChip label={props.label} color={props.color} size="small" />
    </EntityLink>
  );
}
