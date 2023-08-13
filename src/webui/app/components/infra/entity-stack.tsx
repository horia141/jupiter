import { Stack } from "@mui/material";
import { AnimatePresence } from "framer-motion";
import type { PropsWithChildren } from "react";

export function EntityStack(props: PropsWithChildren) {
  return <AnimatePresence>{props.children}</AnimatePresence>;
}

export function EntityStack2(props: PropsWithChildren) {
  return (
    <Stack
      spacing={2}
      sx={{
        marginTop: "-16px",
        "& > :first-child": {
          marginTop: "16px",
        },
      }}
    >
      <AnimatePresence>{props.children}</AnimatePresence>
    </Stack>
  );
}
``;
