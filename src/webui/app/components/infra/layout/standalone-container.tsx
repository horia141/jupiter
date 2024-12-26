import { Stack } from "@mui/material";
import type { PropsWithChildren } from "react";

export function StandaloneContainer(props: PropsWithChildren) {
  return <Stack>{props.children}</Stack>;
}
