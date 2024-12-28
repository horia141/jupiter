import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import DeleteIcon from "@mui/icons-material/Delete";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import SwitchLeftIcon from "@mui/icons-material/SwitchLeft";
import { Box, ButtonGroup, IconButton, Stack, styled } from "@mui/material";
import { Form, Link, useLocation, useNavigate } from "@remix-run/react";
import { motion, useIsPresent } from "framer-motion";
import type { PropsWithChildren } from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  LeafPanelExpansionState,
  loadLeafPanelExpansion,
  saveLeafPanelExpansion,
} from "~/rendering/leaf-panel-expansion";
import {
  restoreScrollPosition,
  saveScrollPosition,
} from "~/rendering/scroll-restoration";
import { useBigScreen } from "~/rendering/use-big-screen";

const BIG_SCREEN_ANIMATION_START = "480px";
const BIG_SCREEN_ANIMATION_END = "480px";

const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

const BIG_SCREEN_WIDTH_SMALL = "480px";
const BIG_SCREEN_WIDTH_MEDIUM = "calc(min(720px, 60vw))";
const BIG_SCREEN_WIDTH_LARGE = "calc(min(1020px, 80vw))";
const BIG_SCREEN_WIDTH_FULL_INT = 1200;
const SMALL_SCREEN_WIDTH = "100%";

interface LeafPanelProps {
  showArchiveButton?: boolean;
  enableArchiveButton?: boolean;
  returnLocation: string;
  initialExpansionState?: LeafPanelExpansionState;
}

export function LeafPanel(props: PropsWithChildren<LeafPanelProps>) {
  const isBigScreen = useBigScreen();
  const navigation = useNavigate();
  const location = useLocation();
  const containerRef = useRef<HTMLDivElement>(null);
  const isPresent = useIsPresent();
  const [expansionState, setExpansionState] = useState(
    props.initialExpansionState ?? LeafPanelExpansionState.SMALL
  );
  const [expansionFullRight, setExpansionFullRight] = useState(0);
  const [expansionFullWidth, setExpansionFullWidth] = useState(
    BIG_SCREEN_WIDTH_FULL_INT
  );

  const handleScroll = useCallback(
    (ref: HTMLDivElement, pathname: string) => {
      if (!isPresent) {
        return;
      }
      saveScrollPosition(ref, pathname);
    },
    [isPresent]
  );

  useEffect(() => {
    if (containerRef.current === null) {
      return;
    }

    const theRef = containerRef.current;

    if (!isPresent) {
      return;
    }

    function handleScrollSpecial() {
      handleScroll(theRef, location.pathname);
    }

    restoreScrollPosition(theRef, location.pathname);
    theRef.addEventListener("scrollend", handleScrollSpecial);

    return () => {
      theRef.removeEventListener("scrollend", handleScrollSpecial);
    };
  }, [containerRef, handleScroll, isPresent, location]);

  // setting right to calc((100vw - BIG_SCREEN_WIDTH_FULL_INT / 2)) doesn't work with framer
  // motion. It seems to be a bug with framer motion. So we have to calculate the right
  // pixel value and then it works.
  function handleChangeExpansionFullRight() {
    setExpansionFullRight(
      Math.max(0, (window.innerWidth - BIG_SCREEN_WIDTH_FULL_INT) / 2)
    );
    setExpansionFullWidth(
      Math.min(BIG_SCREEN_WIDTH_FULL_INT, window.innerWidth)
    );
  }

  useEffect(() => {
    handleChangeExpansionFullRight();
    window.addEventListener("resize", handleChangeExpansionFullRight);

    return () => {
      window.removeEventListener("resize", handleChangeExpansionFullRight);
    };
  }, []);

  function handleExpansion() {
    setExpansionState((e) => cycleExpansionState(e));
    saveLeafPanelExpansion(
      props.returnLocation,
      cycleExpansionState(expansionState)
    );
  }

  useEffect(() => {
    const savedExpansionState = loadLeafPanelExpansion(props.returnLocation);
    if (!savedExpansionState) {
      return;
    }
    setExpansionState(savedExpansionState);
  }, [props.returnLocation]);

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

  const formVariants = {
    initial: {
      opacity: 0,
      x: isBigScreen
        ? BIG_SCREEN_ANIMATION_START
        : SMALL_SCREEN_ANIMATION_START,
    },
    exit: {
      opacity: 0,
      x: isBigScreen ? BIG_SCREEN_ANIMATION_END : SMALL_SCREEN_ANIMATION_END,
    },
    [LeafPanelExpansionState.SMALL]: {
      right: "0px",
      opacity: 1,
      x: 0,
      width: BIG_SCREEN_WIDTH_SMALL,
    },
    [LeafPanelExpansionState.MEDIUM]: {
      right: "0px",
      opacity: 1,
      x: 0,
      width: BIG_SCREEN_WIDTH_MEDIUM,
    },
    [LeafPanelExpansionState.LARGE]: {
      right: "0px",
      opacity: 1,
      x: 0,
      width: BIG_SCREEN_WIDTH_LARGE,
    },
    [LeafPanelExpansionState.FULL]: {
      right: `${expansionFullRight}px`,
      opacity: 1,
      x: 0,
      width: `${expansionFullWidth}px`,
    },
    smallScreen: {
      x: 0,
      opacity: 1,
      width: SMALL_SCREEN_WIDTH,
    },
  };

  return (
    <LeafPanelFrame
      id="leaf-panel"
      key={location.pathname}
      initial="initial"
      animate={isBigScreen ? expansionState : "smallScreen"}
      exit="exit"
      variants={formVariants}
      transition={{ duration: 0.5 }}
      isBigScreen={isBigScreen}
    >
      <Form method="post">
        <LeafPanelControls id="leaf-panel-controls">
          <ButtonGroup size="small">
            {isBigScreen && (
              <IconButton onClick={handleExpansion}>
                <SwitchLeftIcon />
              </IconButton>
            )}
            <IconButton onClick={handleScrollTop}>
              <ArrowUpwardIcon />
            </IconButton>
            <IconButton onClick={handleScrollBottom}>
              <ArrowDownwardIcon />
            </IconButton>
            <IconButton>
              <Link to={props.returnLocation} style={{ display: "flex" }}>
                <KeyboardDoubleArrowRightIcon />
              </Link>
            </IconButton>
            <IconButton onClick={() => navigation(-1)}>
              <ArrowBackIcon />
            </IconButton>
          </ButtonGroup>

          {props.showArchiveButton && (
            <IconButton
              id="leaf-entity-archive"
              sx={{ marginLeft: "auto" }}
              disabled={!props.enableArchiveButton}
              type="submit"
              name="intent"
              value="archive"
            >
              <DeleteIcon />
            </IconButton>
          )}
        </LeafPanelControls>

        <LeafPanelContent
          id="leaf-panel-content"
          ref={containerRef}
          isbigscreen={isBigScreen ? "true" : "false"}
        >
          <Stack spacing={2}>{props.children}</Stack>
          <Box sx={{ height: "4rem" }}></Box>
        </LeafPanelContent>
      </Form>
    </LeafPanelFrame>
  );
}

interface LeafPanelFrameProps {
  isBigScreen: boolean;
}

const LeafPanelFrame = styled(motion.div)<LeafPanelFrameProps>(
  ({ theme, isBigScreen }) => `
      position: ${isBigScreen ? "fixed" : "static"};
      left: ${isBigScreen ? "unset" : "0px"};
      right: 0px;
      bottom: 0px;
      z-index: ${theme.zIndex.appBar + 200};
      background-color: ${theme.palette.background.paper};
      border-left: 1px solid rgba(0, 0, 0, 0.12);
    `
);

const LeafPanelControls = styled("div")(
  ({ theme }) => `
      display: flex;
      padding-left: 0.5rem;
      padding-right: 0.5rem;
      margin-bottom: 1rem;
      height: 3rem;
      background-color: ${theme.palette.background.paper};
      z-index: ${theme.zIndex.drawer + 1};
      border-radius: 0px;
      box-shadow: 0px 5px 5px rgba(0, 0, 0, 0.2);
      `
);

interface LeafPanelContentProps {
  isbigscreen: string;
}

const LeafPanelContent = styled("div")<LeafPanelContentProps>(
  ({ isbigscreen }) => ({
    padding: "0.5rem",
    height: `calc(var(--vh, 1vh) * 100 - env(safe-area-inset-top) - 4rem - ${
      isbigscreen === "true" ? "4rem" : "3.5rem"
    })`,
    overflowY: "scroll",
  })
);

function cycleExpansionState(
  expansionState: LeafPanelExpansionState
): LeafPanelExpansionState {
  switch (expansionState) {
    case LeafPanelExpansionState.SMALL:
      return LeafPanelExpansionState.MEDIUM;
    case LeafPanelExpansionState.MEDIUM:
      return LeafPanelExpansionState.LARGE;
    case LeafPanelExpansionState.LARGE:
      return LeafPanelExpansionState.FULL;
    case LeafPanelExpansionState.FULL:
      return LeafPanelExpansionState.SMALL;
  }
}
