import type { EntityIcon } from "jupiter-gen";

interface EntityIconProps {
  icon: EntityIcon;
}

export default function EntityIconComponent({ icon }: EntityIconProps) {
  return <span>{icon.the_icon}</span>;
}
