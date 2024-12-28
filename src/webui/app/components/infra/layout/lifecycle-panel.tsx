import { Box, Stack } from "@mui/material";
import type { PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";

export function LifecyclePanel(props: PropsWithChildren) {
  const isBigScreen = useBigScreen();
  return (
    <Box
      sx={{
        paddingTop: "4rem",
        width: isBigScreen ? "600px" : "100%",
        height: `calc(var(--vh, 1vh) * 100 - env(safe-area-inset-top) - ${
          isBigScreen ? "4rem" : "3.5rem"
        })`,
        overflowY: "scroll",
        paddingLeft: "1rem",
        paddingRight: "1rem",
        alignSelf: "center",
      }}
    >
      <Stack>
        {props.children}
        <Box sx={{ height: "4rem" }}></Box>
      </Stack>
    </Box>
  );
}
