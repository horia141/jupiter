import { Stack } from "@mui/material";
import type { PropsWithChildren } from "react";

export function BranchCard(props: PropsWithChildren) {
  return (
    <Stack spacing={2} useFlexGap>
      {props.children}
    </Stack>
  );
}
