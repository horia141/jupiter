import type { Project } from "jupiter-gen";
import { SlimChip } from "./infra/slim-chip";

interface Props {
  project: Project;
}

export function ProjectTag(props: Props) {
  return <SlimChip label={props.project.name.the_name} color="info" />;
}
