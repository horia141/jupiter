import { SlimChip } from "./chips";

interface LinkTagProps {
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
  return <SlimChip label={props.label} color={props.color} size="small" />;
}
