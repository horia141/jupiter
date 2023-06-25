import { styled, Toolbar } from "@mui/material";
import { useLocation } from "@remix-run/react";
import { AnimatePresence, motion } from "framer-motion";
import type { PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";

const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

interface ToolPanelProps {
  show: boolean;
}

export function ToolPanel(props: PropsWithChildren<ToolPanelProps>) {
  const isBigScreen = useBigScreen();
  const location = useLocation();

  return (
    <AnimatePresence mode="wait" initial={false}>
      {props.show && (
        <StyledMotionDrawer
          id="tool-panel"
          key={location.pathname}
          isBigScreen={isBigScreen}
          initial={{
            opacity: 0,
            x: isBigScreen ? undefined : SMALL_SCREEN_ANIMATION_START,
          }}
          animate={{ opacity: 1, x: isBigScreen ? undefined : 0 }}
          exit={{
            opacity: 0,
            x: isBigScreen ? undefined : SMALL_SCREEN_ANIMATION_END,
          }}
          transition={{ duration: 0.2 }}
        >
          {!isBigScreen && <Toolbar />}
          {props.children}
        </StyledMotionDrawer>
      )}
    </AnimatePresence>
  );
}

interface StyledMotionDrawerProps {
  isBigScreen: boolean;
}

const StyledMotionDrawer = styled(motion.div)<StyledMotionDrawerProps>(
  ({ theme, isBigScreen }) => {
    if (isBigScreen) {
      return {
        position: "absolute",
        top: "0px",
        width: "100%",
        minHeight: "100%",
        backgroundColor: theme.palette.background.paper,
        zIndex: theme.zIndex.appBar - 2,
        "&::-webkit-scrollbar": {
          display: "none",
        },
      };
    } else {
      return {
        position: "fixed",
        top: "0px",
        right: "0px",
        width: "100%",
        zIndex: theme.zIndex.appBar - 2,
        height: "100%",
        overflowX: "auto",
        overflowY: "scroll",
        backgroundColor: theme.palette.background.paper,
        "&::-webkit-scrollbar": {
          display: "none",
        },
      };
    }
  }
);
