import { styled } from "@mui/material";
import { Form, useLocation, useNavigate } from "@remix-run/react";
import { motion } from "framer-motion";
import type { PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";

const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

interface ToolPanelProps {
  method?: "get" | "post";
}

export function ToolPanel(props: PropsWithChildren<ToolPanelProps>) {
  const isBigScreen = useBigScreen();
  const location = useLocation();
  const navigation = useNavigate();

  return (
    <ToolPanelFrame
      id="tool-panel"
      isBigScreen={isBigScreen}
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
      <ToolCardContent
        isbigscreen={isBigScreen ? "true" : "false"}
        method={props.method || "post"}
      >
        {props.children}
      </ToolCardContent>
    </ToolPanelFrame>
  );
}

interface ToolPanelFrameProps {
  isBigScreen: boolean;
}

const ToolPanelFrame = styled(motion.div)<ToolPanelFrameProps>(
  ({ theme, isBigScreen }) => ({})
);

interface ToolCardContentProps {
  isbigscreen: string;
}

const ToolCardContent = styled(Form)<ToolCardContentProps>(
  ({ isbigscreen }) => ({
    padding: "0.5rem",
    height: `calc(var(--vh, 1vh) * 100 - 4rem - ${
      isbigscreen === "true" ? "4rem" : "3.5rem"
    })`,
    overflowY: "scroll",
  })
);
