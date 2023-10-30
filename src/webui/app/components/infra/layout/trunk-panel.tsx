import { styled } from "@mui/material";
import { useLocation } from "@remix-run/react";
import { motion, useIsPresent } from "framer-motion";
import { PropsWithChildren, useEffect, useRef } from "react";
import { useHydrated } from "remix-utils";
import { extractTrunkFromPath } from "~/rendering/routes";
import {
  restoreScrollPosition,
  saveScrollPosition,
} from "~/rendering/scroll-restoration";
import { useBigScreen } from "~/rendering/use-big-screen";

const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

export function TrunkPanel(props: PropsWithChildren<{}>) {
  const isBigScreen = useBigScreen();
  const location = useLocation();
  const isHydrated = useHydrated();
  const containerRef = useRef<HTMLDivElement>(null);
  const isPresent = useIsPresent();

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

  function handleScroll(ref: HTMLDivElement, pathname: string) {
    if (!isPresent) {
      return;
    }
    saveScrollPosition(ref, pathname);
  }

  useEffect(() => {
    if (containerRef.current === null) {
      return;
    }

    if (!isPresent) {
      return;
    }

    function handleScrollSpecial() {
      handleScroll(
        containerRef.current!,
        extractTrunkFromPath(location.pathname)
      );
    }

    restoreScrollPosition(
      containerRef.current,
      extractTrunkFromPath(location.pathname)
    );
    containerRef.current.addEventListener("scrollend", handleScrollSpecial);

    return () => {
      containerRef.current?.removeEventListener(
        "scrollend",
        handleScrollSpecial
      );
    };
  }, [containerRef, location]);

  return (
    <TrunkCardFrame
      ref={containerRef}
      id="trunk-panel"
      key={extractTrunkFromPath(location.pathname)}
      transformTemplate={template}
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
      transition={{ duration: 0.5 }}
    >
      {props.children}
    </TrunkCardFrame>
  );
}

interface TrunkCardFrameProps {
  isBigScreen: boolean;
}

const TrunkCardFrame = styled(motion.div)<TrunkCardFrameProps>(
  ({ theme, isBigScreen }) => ({
    backgroundColor: theme.palette.background.paper,
    width: isBigScreen ? `${theme.breakpoints.values.lg}px` : "100vw",
    margin: "auto",
    height: isBigScreen ? "calc(var(--vh, 1vh) * 100 - 4rem)" : "calc(var(--vh, 1vh) * 100 - 3.5rem)",
    overflowY: "scroll",
  })
);
