import { AppBar, Toolbar } from "@mui/material";
import type { PropsWithChildren } from "react";

export function SmartAppBar(props: PropsWithChildren) {
  return (
    <AppBar
      position="static"
      sx={{
        paddingTop: "env(safe-area-inset-top)",
        zIndex: (theme) => theme.zIndex.drawer + 10,
      }}
    >
      <Toolbar>{props.children}</Toolbar>
    </AppBar>
  );
}
