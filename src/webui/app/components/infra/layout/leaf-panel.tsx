import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import DeleteIcon from "@mui/icons-material/Delete";
import DeleteForeverIcon from "@mui/icons-material/DeleteForever";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import PictureInPictureAltIcon from "@mui/icons-material/PictureInPictureAlt";
import SwitchLeftIcon from "@mui/icons-material/SwitchLeft";
import {
  Box,
  Button,
  ButtonGroup,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack,
  styled,
} from "@mui/material";
import { Form, useLocation, useNavigate } from "@remix-run/react";
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

const BIG_SCREEN_SHRUNK_HEIGHT = "300px";
const BIG_SCREEN_WIDTH_SMALL = "480px";
const BIG_SCREEN_WIDTH_MEDIUM = "calc(min(720px, 60vw))";
const BIG_SCREEN_WIDTH_LARGE = "calc(min(1020px, 80vw))";
const BIG_SCREEN_WIDTH_FULL_INT = 1200;
const SMALL_SCREEN_WIDTH = "100%";

interface LeafPanelProps {
  showArchiveAndRemoveButton?: boolean;
  inputsEnabled: boolean;
  entityNotEditable?: boolean;
  entityArchived?: boolean;
  returnLocation: string;
  returnLocationDiscriminator?: string;
  initialExpansionState?: LeafPanelExpansionState;
  allowedExpansionStates?: LeafPanelExpansionState[];
}

export function LeafPanel(props: PropsWithChildren<LeafPanelProps>) {
  const isBigScreen = useBigScreen();
  const navigation = useNavigate();
  const location = useLocation();
  const containerRef = useRef<HTMLDivElement>(null);
  const isPresent = useIsPresent();
  const [expansionState, setExpansionState] = useState<
    LeafPanelExpansionState | "shrunk" | "exit"
  >(props.initialExpansionState ?? LeafPanelExpansionState.SMALL);
  const [previousExpansionState, setPreviousExpansionState] =
    useState<LeafPanelExpansionState | null>(null);
  const [expansionFullRight, setExpansionFullRight] = useState(0);
  const [expansionFullWidth, setExpansionFullWidth] = useState(
    BIG_SCREEN_WIDTH_FULL_INT,
  );
  const [showArchiveDialog, setShowArchiveDialog] = useState(false);

  const handleScroll = useCallback(
    (ref: HTMLDivElement, pathname: string) => {
      if (!isPresent) {
        return;
      }
      saveScrollPosition(ref, pathname);
    },
    [isPresent],
  );

  useEffect(() => {
    if (containerRef.current === null) {
      return;
    }

    const theRef = containerRef.current;

    if (!isPresent) {
      return;
    }

    if (location.pathname.endsWith("/new")) {
      return;
    }

    function handleScrollSpecial() {
      handleScroll(theRef, location.pathname);
    }

    restoreScrollPosition(theRef, location.pathname);
    theRef.addEventListener("scroll", handleScrollSpecial);

    return () => {
      theRef.removeEventListener("scroll", handleScrollSpecial);
    };
  }, [containerRef, handleScroll, isPresent, location]);

  // setting right to calc((100vw - BIG_SCREEN_WIDTH_FULL_INT / 2)) doesn't work with framer
  // motion. It seems to be a bug with framer motion. So we have to calculate the right
  // pixel value and then it works.
  function handleChangeExpansionFullRight() {
    setExpansionFullRight(
      Math.max(0, (window.innerWidth - BIG_SCREEN_WIDTH_FULL_INT) / 2),
    );
    setExpansionFullWidth(
      Math.min(BIG_SCREEN_WIDTH_FULL_INT, window.innerWidth),
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
    setExpansionState((e) =>
      cycleExpansionState(e, props.allowedExpansionStates),
    );
    saveLeafPanelExpansion(
      `${props.returnLocation}/${props.returnLocationDiscriminator}`,
      cycleExpansionState(expansionState, props.allowedExpansionStates),
    );
  }

  useEffect(() => {
    const savedExpansionState = loadLeafPanelExpansion(
      `${props.returnLocation}/${props.returnLocationDiscriminator}`,
    );
    if (!savedExpansionState) {
      return;
    }
    setExpansionState(savedExpansionState);
  }, [props.returnLocation, props.returnLocationDiscriminator]);

  function handleShrunk() {
    if (expansionState !== "shrunk" && expansionState !== "exit") {
      setPreviousExpansionState(expansionState);
      setExpansionState("shrunk");
    } else {
      setExpansionState(previousExpansionState as LeafPanelExpansionState);
      setPreviousExpansionState(null);
    }
  }

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
      width: "0px",
    },
    [LeafPanelExpansionState.SMALL]: {
      right: "0px",
      opacity: 1,
      x: 0,
      width: BIG_SCREEN_WIDTH_SMALL,
      height: `calc(var(--vh, 1vh) * 100 - env(safe-area-inset-top) - 4rem)`,
    },
    [LeafPanelExpansionState.MEDIUM]: {
      right: "0px",
      opacity: 1,
      x: 0,
      width: BIG_SCREEN_WIDTH_MEDIUM,
      height: `calc(var(--vh, 1vh) * 100 - env(safe-area-inset-top) - 4rem)`,
    },
    [LeafPanelExpansionState.LARGE]: {
      right: "0px",
      opacity: 1,
      x: 0,
      width: BIG_SCREEN_WIDTH_LARGE,
      height: `calc(var(--vh, 1vh) * 100 - env(safe-area-inset-top) - 4rem)`,
    },
    [LeafPanelExpansionState.FULL]: {
      right: `${expansionFullRight}px`,
      opacity: 1,
      x: 0,
      width: `${expansionFullWidth}px`,
      height: `calc(var(--vh, 1vh) * 100 - env(safe-area-inset-top) - 4rem)`,
    },
    smallScreen: {
      x: 0,
      opacity: 1,
      width: SMALL_SCREEN_WIDTH,
    },
    shrunk: {
      x: 0,
      opacity: 1,
      height: BIG_SCREEN_SHRUNK_HEIGHT,
      width: BIG_SCREEN_WIDTH_SMALL,
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
              <>
                <IconButton
                  disabled={expansionState === "shrunk"}
                  onClick={handleExpansion}
                >
                  <SwitchLeftIcon />
                </IconButton>
                <IconButton onClick={handleShrunk}>
                  <PictureInPictureAltIcon />
                </IconButton>
              </>
            )}
            <IconButton onClick={handleScrollTop}>
              <ArrowUpwardIcon />
            </IconButton>
            <IconButton onClick={handleScrollBottom}>
              <ArrowDownwardIcon />
            </IconButton>
            <IconButton
              onClick={() => {
                setExpansionState("exit");
                const returnLocation = props.returnLocation;
                setTimeout(() => navigation(returnLocation), 500);
              }}
            >
              <KeyboardDoubleArrowRightIcon />
            </IconButton>
            <IconButton
              onClick={() => {
                setExpansionState("exit");
                setTimeout(() => navigation(-1), 500);
              }}
            >
              <ArrowBackIcon />
            </IconButton>
          </ButtonGroup>

          {props.showArchiveAndRemoveButton && (
            <>
              <IconButton
                id="leaf-entity-archive"
                sx={{ marginLeft: "auto" }}
                disabled={
                  props.entityNotEditable ||
                  (!props.entityArchived && !props.inputsEnabled)
                }
                type="button"
                onClick={() => setShowArchiveDialog(true)}
              >
                {props.entityArchived ? <DeleteForeverIcon /> : <DeleteIcon />}
              </IconButton>
              <Dialog
                onClose={() => setShowArchiveDialog(false)}
                open={showArchiveDialog}
                disablePortal
              >
                <DialogTitle>Careful!</DialogTitle>
                <DialogContent>
                  Are you sure you want to{" "}
                  {props.entityArchived ? "remove" : "archive"} this entity?
                  {props.entityArchived ? " This action cannot be undone." : ""}
                </DialogContent>
                <DialogActions>
                  <Button
                    id="leaf-entity-archive-confirm"
                    sx={{ marginLeft: "auto" }}
                    disabled={
                      props.entityNotEditable ||
                      (!props.entityArchived && !props.inputsEnabled)
                    }
                    type="submit"
                    name="intent"
                    value={props.entityArchived ? "remove" : "archive"}
                  >
                    Yes
                  </Button>
                  <Button onClick={() => setShowArchiveDialog(false)}>
                    No
                  </Button>
                </DialogActions>
              </Dialog>
            </>
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
    `,
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
      `,
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
  }),
);

function cycleExpansionState(
  expansionState: LeafPanelExpansionState | "shrunk" | "exit",
  allowedExpansionStates?: LeafPanelExpansionState[],
): LeafPanelExpansionState {
  if (expansionState === "shrunk" || expansionState === "exit") {
    return LeafPanelExpansionState.SMALL;
  }
  if (allowedExpansionStates && allowedExpansionStates.length > 0) {
    const currentIndex = allowedExpansionStates.indexOf(expansionState);
    const nextIndex = (currentIndex + 1) % allowedExpansionStates.length;
    return allowedExpansionStates[nextIndex];
  }

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
