import { AnimatePresence } from "framer-motion";
import type { PropsWithChildren } from "react";

export function EntityStack(props: PropsWithChildren) {
  return <AnimatePresence>{props.children}</AnimatePresence>;
}
