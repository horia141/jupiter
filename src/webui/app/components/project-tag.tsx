import type { Project } from "@jupiter/webapi-client";

import { SlimChip } from "./infra/chips";

interface Props {
  project: Project;
}

export function ProjectTag(props: Props) {
  return <SlimChip label={props.project.name} color="info" />;
}
