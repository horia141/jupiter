import { SlimChip } from "#/core/infra/component/chips";

interface IsSuspendedTagProps {
  isSuspended: boolean;
}

export function IsSuspendedTag({ isSuspended }: IsSuspendedTagProps) {
  if (!isSuspended) return null;

  return (
    <SlimChip
      label="Suspended"
      color="warning"
      sx={{ flexShrink: 0, whiteSpace: "nowrap" }}
    />
  );
}
