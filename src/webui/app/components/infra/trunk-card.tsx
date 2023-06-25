import { Stack } from "@mui/material";
import type { PropsWithChildren } from "react";

export function TrunkCard(props: PropsWithChildren) {
  return (
    <Stack spacing={2} useFlexGap>
      {props.children}
    </Stack>
  );
}
