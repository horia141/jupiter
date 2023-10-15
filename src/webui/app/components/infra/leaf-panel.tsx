import { styled, Toolbar } from "@mui/material";
import { useLocation } from "@remix-run/react";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, type PropsWithChildren, useRef } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";

const BIG_SCREEN_WIDTH = "480px";
const BIG_SCREEN_ANIMATION_START = "480px";
const BIG_SCREEN_ANIMATION_END = "480px";
const SMALL_SCREEN_WIDTH = "100%";
const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

interface LeafPanelProps {
  show: boolean;
}

export function LeafPanel(props: PropsWithChildren<LeafPanelProps>) {
  const isBigScreen = useBigScreen();
  const location = useLocation();

  const drawerRef = useRef<HTMLDivElement>(null);

  function handleScroll() {
    if (isBigScreen) {
    window.sessionStorage.setItem(`scroll:${location.pathname}`, `${drawerRef.current?.scrollTop}`);
    } else {
      window.sessionStorage.setItem(`scroll:${location.pathname}`, `${window.pageYOffset}`);
    }
  }

  useEffect(() => {
    if (drawerRef.current === null) {
      return;
    }

    if (isBigScreen) {
    drawerRef.current.addEventListener('scroll', handleScroll);
    drawerRef.current.scrollTo(0, parseInt(window.sessionStorage.getItem(`scroll:${location.pathname}`) ?? '0'));

    } else {
      window.addEventListener('scroll', handleScroll);
      window.scrollTo(0, parseInt(window.sessionStorage.getItem(`scroll:${location.pathname}`) ?? '0'));
    }

    return () => {
      drawerRef.current?.removeEventListener('scroll', handleScroll);
      window.removeEventListener('scroll', handleScroll);
    }
  }, [isBigScreen]);

  return (
    <AnimatePresence mode="wait" initial={false}>
      {props.show && (
        <StyledMotionDrawer
          ref={drawerRef}
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
          {isBigScreen && <Toolbar />}
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
    top: 0px;
    right: 0px;
    bottom: 0px;
    width: ${isBigScreen ? BIG_SCREEN_WIDTH : SMALL_SCREEN_WIDTH};
    z-index: ${theme.zIndex.appBar - 1};
    overflow-y: ${isBigScreen ? "scroll" : "inherit"};
    background-color: ${theme.palette.background.paper};
    border-left: 1px solid rgba(0, 0, 0, 0.12);

    &::-webkit-scrollbar {
      display: none;
    }
  `
);
