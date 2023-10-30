import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import DeleteIcon from "@mui/icons-material/Delete";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import SwitchLeftIcon from "@mui/icons-material/SwitchLeft";
import { ButtonGroup, IconButton, styled, useTheme } from "@mui/material";
import { Form, Link, useLocation, useNavigate } from "@remix-run/react";
import { motion, useIsPresent } from "framer-motion";
import { PropsWithChildren, useEffect, useRef, useState } from "react";
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

export enum LeafCardExpansionState {
  SMALL = "small",
  MEDIUM = "medium",
  LARGE = "large",
  FULL = "full",
}

interface LeafCardProps {
  showArchiveButton?: boolean;
  enableArchiveButton?: boolean;
  returnLocation: string;
  initialExpansionState?: LeafCardExpansionState;
}

export function LeafPanel(props: PropsWithChildren<LeafCardProps>) {
  const theme = useTheme();
  const isBigScreen = useBigScreen();
  const navigation = useNavigate();
  const location = useLocation();
  const containerRef = useRef<HTMLFormElement>(null);
  const isPresent = useIsPresent();
  const [expansionState, setExpansionState] = useState(
    props.initialExpansionState ?? LeafCardExpansionState.SMALL
  );
  const [expansionFullRight, setExpansionFullRight] = useState(0);
  const [expansionFullWidth, setExpansionFullWidth] = useState(
    BIG_SCREEN_WIDTH_FULL_INT
  );

  function handleScroll(ref: HTMLFormElement, pathname: string) {
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
      handleScroll(containerRef.current!, location.pathname);
    }

    restoreScrollPosition(containerRef.current, location.pathname);
    containerRef.current.addEventListener("scrollend", handleScrollSpecial);

    return () => {
      containerRef.current?.removeEventListener(
        "scrollend",
        handleScrollSpecial
      );
    };
  }, [containerRef, location]);

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
    [LeafCardExpansionState.SMALL]: {
      right: "0px",
      opacity: 1,
      x: 0,
      width: BIG_SCREEN_WIDTH_SMALL,
    },
    [LeafCardExpansionState.MEDIUM]: {
      right: "0px",
      opacity: 1,
      x: 0,
      width: BIG_SCREEN_WIDTH_MEDIUM,
    },
    [LeafCardExpansionState.LARGE]: {
      right: "0px",
      opacity: 1,
      x: 0,
      width: BIG_SCREEN_WIDTH_LARGE,
    },
    [LeafCardExpansionState.FULL]: {
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
    <LeafCardFrame
      id="leaf-panel"
      key={location.pathname}
      initial="initial"
      animate={isBigScreen ? expansionState : "smallScreen"}
      exit="exit"
      variants={formVariants}
      transition={{ duration: 0.5 }}
      isBigScreen={isBigScreen}
    >
      <LeafCardControls id="leaf-panel-controls">
        <ButtonGroup size="small">
          {isBigScreen && (
            <IconButton
              onClick={() => setExpansionState((e) => cycleExpansionState(e))}
            >
              <SwitchLeftIcon />
            </IconButton>
          )}
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
            sx={{ marginLeft: "auto" }}
            disabled={!props.enableArchiveButton}
            type="submit"
            name="intent"
            value="archive"
          >
            <DeleteIcon />
          </IconButton>
        )}
      </LeafCardControls>

      <LeafCardContent
        id="leaf-panel-content"
        method="post"
        ref={containerRef}
        isbigscreen={isBigScreen ? "true" : "false"}
      >
        {props.children}
      </LeafCardContent>
    </LeafCardFrame>
  );
}

interface LeafCardFrameProps {
  isBigScreen: boolean;
}

const LeafCardFrame = styled(motion.div)<LeafCardFrameProps>(
  ({ theme, isBigScreen }) => `
      position: ${isBigScreen ? "fixed" : "static"};
      left: ${isBigScreen ? "unset" : "0px"};
      right: 0px;
      bottom: 0px;
      z-index: ${theme.zIndex.appBar - 1};
      background-color: ${theme.palette.background.paper};
      border-left: 1px solid rgba(0, 0, 0, 0.12);
    `
);

const LeafCardControls = styled("div")(
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

interface LeafCardContentProps {
  isbigscreen: string;
}

const LeafCardContent = styled(Form)<LeafCardContentProps>(
  ({ isbigscreen }) => ({
    padding: "0.5rem",
    height: `calc(var(--vh, 1vh) * 100 - 4rem - ${
      isbigscreen === "true" ? "4rem" : "3.5rem"
    })`,
    overflowY: "scroll",
  })
);

function cycleExpansionState(
  expansionState: LeafCardExpansionState
): LeafCardExpansionState {
  switch (expansionState) {
    case LeafCardExpansionState.SMALL:
      return LeafCardExpansionState.MEDIUM;
    case LeafCardExpansionState.MEDIUM:
      return LeafCardExpansionState.LARGE;
    case LeafCardExpansionState.LARGE:
      return LeafCardExpansionState.FULL;
    case LeafCardExpansionState.FULL:
      return LeafCardExpansionState.SMALL;
  }
}
