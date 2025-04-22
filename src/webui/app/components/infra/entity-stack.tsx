import { Stack } from "@mui/material";
import { AnimatePresence } from "framer-motion";
import type { PropsWithChildren } from "react";

export function EntityStack(props: PropsWithChildren) {
  return <AnimatePresence>{props.children}</AnimatePresence>;
}

interface EntityStackProps {
  id?: string;
}

export function EntityStack2(props: PropsWithChildren<EntityStackProps>) {
  return (
    <Stack
      id={props.id}
      spacing={2}
      sx={{
        marginTop: "-8px",
        "& > :first-child": {
          marginTop: "8px",
        },
      }}
    >
      <AnimatePresence>{props.children}</AnimatePresence>
    </Stack>
  );
}
