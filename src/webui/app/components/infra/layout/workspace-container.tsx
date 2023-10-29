import { Stack } from "@mui/material";
import type { PropsWithChildren } from "react";

export function WorkspaceContainer(props: PropsWithChildren) {
  return (
    <Stack useFlexGap gap={0}>
      {props.children}
    </Stack>
  );
}
