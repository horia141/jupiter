import { Box, styled } from "@mui/material";
import { useLocation } from "@remix-run/react";
import { motion } from "framer-motion";
import type { PropsWithChildren } from "react";

import { useBigScreen } from "~/rendering/use-big-screen";

const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

export function ToolPanel(props: PropsWithChildren) {
  const isBigScreen = useBigScreen();
  const location = useLocation();

  return (
    <ToolPanelFrame
      id="tool-panel"
      key={location.pathname}
      initial={{
        opacity: 0,
        x: isBigScreen ? undefined : SMALL_SCREEN_ANIMATION_START,
      }}
      animate={{ opacity: 1, x: isBigScreen ? undefined : 0 }}
      exit={{
        opacity: 0,
        x: isBigScreen ? undefined : SMALL_SCREEN_ANIMATION_END,
      }}
      transition={{ duration: 0.5 }}
    >
      <ToolCardContent isbigscreen={isBigScreen ? "true" : "false"}>
        {props.children}
      </ToolCardContent>
    </ToolPanelFrame>
  );
}

const ToolPanelFrame = styled(motion.div)(() => ({}));

interface ToolCardContentProps {
  isbigscreen: string;
}

const ToolCardContent = styled(Box)<ToolCardContentProps>(
  ({ isbigscreen }) => ({
    padding: "0.5rem",
    height: `calc(var(--vh, 1vh) * 100 - env(safe-area-inset-top) - 4rem - ${
      isbigscreen === "true" ? "4rem" : "3.5rem"
    })`,
    overflowY: "scroll",
  }),
);
