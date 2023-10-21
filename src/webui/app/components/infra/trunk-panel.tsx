import { styled } from "@mui/material";
import { useLocation } from "@remix-run/react";
import { AnimatePresence, motion } from "framer-motion";
import { type PropsWithChildren } from "react";
import { extractTrunkFromPath } from "~/rendering/routes";
import { useBigScreen } from "~/rendering/use-big-screen";

const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

interface TrunkPanelProps {
  show: boolean;
}

export function TrunkPanel(props: PropsWithChildren<TrunkPanelProps>) {
  const isBigScreen = useBigScreen();
  const location = useLocation();

  return (
    <AnimatePresence mode="wait" initial={false}>
      {props.show && (
        <StyledMotionDrawer
          id="trunk-panel"
          key={extractTrunkFromPath(location.pathname)}
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
  ({ theme, isBigScreen }) => ({
    backgroundColor: theme.palette.background.paper,
    width: "100vw",
    height: isBigScreen ? "calc(100vh - 4rem)" : "calc(100vh - 3.5rem)",

    "&::-webkit-scrollbar": {
      display: "none",
    },
  })
);
