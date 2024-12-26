import { Stack } from "@mui/material";
import type { PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";

export function LifecyclePanel(props: PropsWithChildren) {
  const isBigScreen = useBigScreen();
  return (
    <Stack
      sx={{
        paddingTop: "4rem",
        width: isBigScreen ? "600px" : "100%",
        paddingLeft: "1rem",
        paddingRight: "1rem",
        alignSelf: "center",
      }}
    >
      {props.children}
    </Stack>
  );
}
