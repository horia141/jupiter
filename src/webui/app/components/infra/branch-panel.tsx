import { styled } from "@mui/material";
import { useLocation } from "@remix-run/react";
import { AnimatePresence, motion } from "framer-motion";
import type { PropsWithChildren } from "react";
import { useHydrated } from "remix-utils";
import { extractBranchFromPath } from "~/rendering/routes";
import { useBigScreen } from "~/rendering/use-big-screen";

const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

interface BranchPanelProps {
  show: boolean;
}

export function BranchPanel(props: PropsWithChildren<BranchPanelProps>) {
  const isBigScreen = useBigScreen();
  const location = useLocation();
  const isHydrated = useHydrated();

  // This little function is a hack to get around the fact that Framer Motion
  // generates a translateX(Xpx) CSS applied to the StyledMotionDrawer element.
  // This in turns causes browers to make this div be container for any inner
  // child who is position: fixed. This is a problem because we want such elements
  // to be relative to the viewport, not this element. So we use this function to
  // not emit a translateX in case of 0px. So whenever any leaf element appears
  // it'll work relative to the whole viewport.
  function template({ x }: { x: string }, generatedTransform: string): string {
    if (x === "0px" || x === "0vw" || x === "0%" || x === "0") {
      if (isHydrated) {
        return "";
      } else {
        return undefined as unknown as string;
      }
    }
    return `translateX(${x})`;
  }

  return (
    <AnimatePresence mode="wait" initial={false}>
      {props.show && (
        <StyledMotionDrawer
          id="branch-panel"
          key={extractBranchFromPath(location.pathname)}
          transformTemplate={template}
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
  ({isBigScreen}) => `
  width: ${isBigScreen ? "100vw" : "auto"};
  height: ${isBigScreen ? "100vh" : "auto"};
    &::-webkit-scrollbar {
      display: none;
    }
  `
);
