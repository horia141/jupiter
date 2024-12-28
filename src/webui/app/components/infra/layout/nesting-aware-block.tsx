import { Box, Stack } from "@mui/material";
import type { PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";

interface NestingAwarePanelProps {
  shouldHide: boolean;
  branchForceHide?: boolean;
}

export function NestingAwareBlock(
  props: PropsWithChildren<NestingAwarePanelProps>
) {
  const isBigScreen = useBigScreen();

  if (!isBigScreen && props.shouldHide) {
    return null;
  }

  if (props.branchForceHide) {
    return null;
  }

  return (
    <Stack
      spacing={2}
      useFlexGap
      sx={{ paddingLeft: "1rem", paddingRight: "1rem" }}
    >
      {props.children}
      <Box sx={{ height: "4rem" }}></Box>
    </Stack>
  );
}
