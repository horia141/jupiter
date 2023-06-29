import { Stack } from "@mui/system";
import { PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";

interface NestingAwarePanelProps {
  showOutlet: boolean;
  branchForceHide?: boolean;
}

export function NestingAwarePanel(
  props: PropsWithChildren<NestingAwarePanelProps>
) {
  const isBigScreen = useBigScreen();

  if (props.branchForceHide) {
    return null;
  }

  if (isBigScreen) {
    return (
      <Stack spacing={2} useFlexGap>
        {props.children}
      </Stack>
    );
  } else {
    if (!props.showOutlet) {
      return (
        <Stack
          spacing={2}
          useFlexGap
          sx={{ paddingLeft: "1rem", paddingRight: "1rem" }}
        >
          {props.children}
        </Stack>
      );
    } else {
      return null;
    }
  }
}