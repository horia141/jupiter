import type { EntityIcon } from "webapi-client";

interface EntityIconProps {
  icon: EntityIcon;
}

export default function EntityIconComponent({ icon }: EntityIconProps) {
  return <span>{icon}</span>;
}
