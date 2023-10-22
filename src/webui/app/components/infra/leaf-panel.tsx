import { styled } from "@mui/material";
import { useLocation } from "@remix-run/react";
import { AnimatePresence, motion } from "framer-motion";
import { type PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";


const BIG_SCREEN_ANIMATION_START = "480px";
const BIG_SCREEN_ANIMATION_END = "480px";

const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

interface LeafPanelProps {
  show: boolean;
}

export function LeafPanel(props: PropsWithChildren<LeafPanelProps>) {
  const isBigScreen = useBigScreen();
  const location = useLocation();

  return (
    <AnimatePresence mode="wait" initial={false}>
      {props.show && (
        <StyledMotionDrawer
          id="leaf-panel"
          key={location.pathname}
          initial={{
            opacity: 0,
            x: isBigScreen
              ? BIG_SCREEN_ANIMATION_START
              : SMALL_SCREEN_ANIMATION_START,
          }}
          animate={{ opacity: 1, x: 0 }}
          exit={{
            opacity: 0,
            x: isBigScreen
              ? BIG_SCREEN_ANIMATION_END
              : SMALL_SCREEN_ANIMATION_END,
          }}
          transition={{ duration: 0.2 }}
          isBigScreen={isBigScreen}
        >
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
  ({ theme, isBigScreen }) => `
    position: ${isBigScreen ? "fixed" : "relative"};
    top: ${isBigScreen ? "4rem" : "0px"};
    right: 0px;
    bottom: 0px;
    z-index: ${theme.zIndex.appBar - 1};
    background-color: ${theme.palette.background.paper};
    border-left: 1px solid rgba(0, 0, 0, 0.12);
  `
);
