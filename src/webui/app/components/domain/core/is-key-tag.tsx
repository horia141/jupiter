import { SlimChip } from "~/components/infra/chips";

interface IsKeyTagProps {
  isKey: boolean;
}

export function IsKeyTag({ isKey }: IsKeyTagProps) {
  if (!isKey) return null;

  return <SlimChip label="🔑" color="default" />;
}
