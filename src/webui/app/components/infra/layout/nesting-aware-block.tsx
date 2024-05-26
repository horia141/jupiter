import { Stack } from "@mui/system";
import { Form } from "@remix-run/react";
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
      <Form method="post">{props.children}</Form>
    </Stack>
  );
}
