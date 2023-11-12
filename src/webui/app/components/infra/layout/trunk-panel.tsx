import AddIcon from "@mui/icons-material/Add";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import CloseIcon from "@mui/icons-material/Close";
import MoreHorizIcon from "@mui/icons-material/MoreHoriz";
import { Box, Button, ButtonGroup, IconButton, styled } from "@mui/material";
import { Link, useLocation } from "@remix-run/react";
import { AnimatePresence, motion, useIsPresent } from "framer-motion";
import React, { PropsWithChildren, useEffect, useRef, useState } from "react";
import { useHydrated } from "remix-utils";
import { extractTrunkFromPath } from "~/rendering/routes";
import {
  restoreScrollPosition,
  saveScrollPosition,
} from "~/rendering/scroll-restoration";
import { useBigScreen } from "~/rendering/use-big-screen";
import {
  useTrunkNeedsToShowBranch,
  useTrunkNeedsToShowLeaf,
} from "~/rendering/use-nested-entities";

const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

interface TrunkPanelProps {
  createLocation?: string;
  extraControls?: JSX.Element[];
  returnLocation: string;
}

export function TrunkPanel(props: PropsWithChildren<TrunkPanelProps>) {
  const isBigScreen = useBigScreen();
  const location = useLocation();
  const isHydrated = useHydrated();
  const containerRef = useRef<HTMLDivElement>(null);
  const isPresent = useIsPresent();
  const shouldShowALeaf = useTrunkNeedsToShowLeaf();
  const shouldShowABranch = useTrunkNeedsToShowBranch();

  // This little function is a hack to get around the fact that Framer Motion
  // generates a translateX(Xpx) CSS applied to the StyledMotionDrawer element.
  // This in turns causes browers to make this div be container for any inner
  // child who is position: fixed. This is a problem because we want such elements
  // to be relative to the viewport, not this element. So we use this function to
  // not emit a translateX in case of 0px. So whenever any trunk element appears
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
  }, [containerRef, location, isBigScreen]);

  function handleScrollTop() {
    containerRef.current?.scrollTo({
      left: 0,
      top: 0,
      behavior: "smooth",
    });
  }

  function handleScrollBottom() {
    if (!containerRef.current) {
      return;
    }

    containerRef.current.scrollTo({
      left: 0,
      top: containerRef.current.scrollHeight,
      behavior: "smooth",
    });
  }

  return (
    <TrunkPanelFrame
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
      {!shouldShowABranch && (isBigScreen || !shouldShowALeaf) && (
        <TrunkPanelControls id="trunk-panel-controls">
          <TrunkPanelControlsInner isbigscreen={isBigScreen ? "true" : "false"}>
            <ButtonGroup size="small">
              <IconButton onClick={handleScrollTop}>
                <ArrowUpwardIcon />
              </IconButton>
              <IconButton onClick={handleScrollBottom}>
                <ArrowDownwardIcon />
              </IconButton>
            </ButtonGroup>

            {props.createLocation && (
              <Button
                variant="contained"
                to={props.createLocation}
                component={Link}
              >
                <AddIcon />
              </Button>
            )}

            {props.extraControls && (
              <TrunkPanelExtraControls
                isBigScreen={isBigScreen}
                controls={props.extraControls}
              />
            )}

            <IconButton sx={{ marginLeft: "auto" }}>
              <Link to={props.returnLocation}>
                <CloseIcon />
              </Link>
            </IconButton>
          </TrunkPanelControlsInner>
        </TrunkPanelControls>
      )}

      <TrunkPanelContent
        id="trunk-panel-content"
        ref={containerRef}
        isbigscreen={isBigScreen ? "true" : "false"}
        hasbranch={shouldShowABranch ? "true" : "false"}
        hasleaf={shouldShowALeaf ? "true" : "false"}
      >
        {props.children}
      </TrunkPanelContent>
    </TrunkPanelFrame>
  );
}

interface TrunkPanelFrameProps {
  isBigScreen: boolean;
}

const TrunkPanelFrame = styled(motion.div)<TrunkPanelFrameProps>(
  ({ theme, isBigScreen }) => ({
    backgroundColor: theme.palette.background.paper,
    width: "100vw",
  })
);

const TrunkPanelControls = styled("div")(
  ({ theme }) => `
      margin-bottom: 1rem;
      height: 3rem;
      background-color: ${theme.palette.background.paper};
      border-radius: 0px;
      box-shadow: 0px 5px 5px rgba(0, 0, 0, 0.2);
      `
);

interface TrunkPanelControlsInnerProps {
  isbigscreen: string;
}

const TrunkPanelControlsInner = styled(Box)<TrunkPanelControlsInnerProps>(
  ({ theme, isbigscreen }) => ({
    width:
      isbigscreen === "true" ? `${theme.breakpoints.values.lg}px` : "100vw",
    margin: "auto",
    display: "flex",
    alignItems: "center",
    gap: "1rem",
  })
);

interface TrunkPanelExtraControlsProps {
  isBigScreen: boolean;
  controls: JSX.Element[];
}

function TrunkPanelExtraControls({
  isBigScreen,
  controls,
}: TrunkPanelExtraControlsProps) {
  const [showFullControls, setShowFullControls] = useState(false);

  if (isBigScreen) {
    return (
      <>
        {controls.map((c, i) => (
          <React.Fragment key={i}>{c}</React.Fragment>
        ))}
      </>
    );
  } else if (controls.length === 0) {
    return null;
  } else if (controls.length === 1) {
    return controls[0];
  }

  return (
    <>
      {!showFullControls && (
        <Button variant="outlined" onClick={() => setShowFullControls(true)}>
          <MoreHorizIcon />
        </Button>
      )}
      <AnimatePresence>
        {showFullControls && (
          <TrunkPanelExtraControlsFrame
            key="trunk-panel-extra-controls"
            initial={{ opacity: 1, x: "100vw" }}
            animate={{ opacity: 1, x: "0vw" }}
            exit={{ opacity: 1, x: "100vw" }}
            transition={{ duration: 0.4 }}
          >
            <TrunkPanelExtraControlsOuterContainer>
              <TrunkPanelExtraControlsInnerContainer>
                {controls.map((c, i) => (
                  <React.Fragment key={i}>{c}</React.Fragment>
                ))}
              </TrunkPanelExtraControlsInnerContainer>
            </TrunkPanelExtraControlsOuterContainer>
            <IconButton
              onClick={() => setShowFullControls(false)}
              sx={{ marginLeft: "auto" }}
            >
              <CloseIcon />
            </IconButton>
          </TrunkPanelExtraControlsFrame>
        )}
      </AnimatePresence>
    </>
  );
}

const TrunkPanelExtraControlsFrame = styled(motion.div)(() => ({
  position: "absolute",
  left: "0px",
  right: "0px",
  height: "3rem",
  backgroundColor: "white",
  width: "100vw",
  display: "flex",
  paddingLeft: "0.5rem",
  paddingRight: "0.5rem",
  alignItems: "center",
  zIndex: "1002",
}));

const TrunkPanelExtraControlsOuterContainer = styled(Box)(() => ({
  width: "calc(100vw - 1rem - 1rem - 16px)",
  overflowX: "scroll",
}));

const TrunkPanelExtraControlsInnerContainer = styled(Box)(() => ({
  display: "flex",
  gap: "1rem",
  width: "fit-content",
}));

interface TrunkPanelContentProps {
  isbigscreen: string;
  hasbranch: string;
  hasleaf: string;
}

const TrunkPanelContent = styled("div")<TrunkPanelContentProps>(
  ({ theme, isbigscreen, hasleaf, hasbranch }) => ({
    width:
      hasbranch === "false"
        ? isbigscreen === "true"
          ? `${theme.breakpoints.values.lg}px`
          : "100vw"
        : "100vw",
    margin: "auto",
    padding:
      hasbranch === "false"
        ? isbigscreen === "true"
          ? "0.5rem"
          : "0px"
        : "0px",
    height: `calc(var(--vh, 1vh) * 100 - ${
      isbigscreen === "true" ? "4rem" : "3.5rem"
    } - ${
      hasbranch === "false"
        ? isbigscreen === "true"
          ? "4rem"
          : hasleaf === "false"
          ? "4rem"
          : "0px"
        : "0px"
    })`,
    overflowY: "scroll",
  })
);
