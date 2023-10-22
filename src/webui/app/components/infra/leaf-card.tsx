import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import DeleteIcon from "@mui/icons-material/Delete";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import { ButtonGroup, IconButton, styled, useTheme } from "@mui/material";
import { Form, Link, useLocation, useNavigate } from "@remix-run/react";
import SwitchLeftIcon from '@mui/icons-material/SwitchLeft';
import { motion, useIsPresent } from "framer-motion";
import { useEffect, useRef, type PropsWithChildren, useState } from "react";
import {
  restoreScrollPosition,
  saveScrollPosition,
} from "~/rendering/scroll-restoration";
import { useBigScreen } from "~/rendering/use-big-screen";

const BIG_SCREEN_WIDTH_SMALL = "480px";
const BIG_SCREEN_WIDTH_MEDIUM = "calc(min(720px, 60vw))";
const BIG_SCREEN_WIDTH_LARGE = "calc(min(1020px, 80vw))";
const BIG_SCREEN_WIDTH_FULL = "1200px";
const SMALL_SCREEN_WIDTH = "100%";

export enum LeafCardExpansionState {
  SMALL = "small",
  MEDIUM = "medium",
  LARGE = "large",
  FULL = "full"
}

interface LeafCardProps {
  showArchiveButton?: boolean;
  enableArchiveButton?: boolean;
  returnLocation: string;
  initialExpansionState?: LeafCardExpansionState;
}

export function LeafCard(props: PropsWithChildren<LeafCardProps>) {
  const theme = useTheme();
  const isBigScreen = useBigScreen();
  const navigation = useNavigate();
  const location = useLocation();
  const containerRef = useRef<HTMLDivElement>(null);
  const isPresent = useIsPresent();
  const [expansionState, setExpansionState] = useState(props.initialExpansionState ?? LeafCardExpansionState.SMALL);

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

  const formVariants = {
    [LeafCardExpansionState.SMALL]: {
      right: "0px"
    },
    [LeafCardExpansionState.MEDIUM]: {
      right: "0px"
    },
    [LeafCardExpansionState.LARGE]: {
      right: "0px"
    },
    [LeafCardExpansionState.FULL]: {
      right: `calc((100vw - ${BIG_SCREEN_WIDTH_FULL}) / 2)`
    }
  }

  const containerVariants = {
    [LeafCardExpansionState.SMALL]: {
      width: BIG_SCREEN_WIDTH_SMALL
    },
    [LeafCardExpansionState.MEDIUM]: {
      width: BIG_SCREEN_WIDTH_MEDIUM
    },
    [LeafCardExpansionState.LARGE]: {
      width: BIG_SCREEN_WIDTH_LARGE
    },
    [LeafCardExpansionState.FULL]: {
      width: BIG_SCREEN_WIDTH_FULL
    },
    smallScreen: {
      width: SMALL_SCREEN_WIDTH
    }
  };

  return (
    <Form method="post">
      <motion.div
        style={{backgroundColor: theme.palette.background.paper,
        position: "relative", right: "0px"}}
        initial={false}
        animate={isBigScreen ? expansionState : "small"}
        variants={formVariants}
        transition={{duration: 0.2}}
        >
      <StyledButtonGroup>
        <ButtonGroup size="small">
          {isBigScreen && <IconButton onClick={() => setExpansionState((e) => cycleExpansionState(e))}>
              <SwitchLeftIcon />
          </IconButton>}
          <IconButton>
            <Link to={props.returnLocation} style={{display: "flex"}}>
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
      </StyledButtonGroup>
      <motion.div
        ref={containerRef}
        animate={isBigScreen ? expansionState : "smallScreen"}
        variants={containerVariants}
        transition={{ duration: 0.2 }}
        style={{
          padding: "0.5rem",
          height: `calc(100vh - 4rem - ${isBigScreen ? "4rem" : "3.5rem"})`,
          overflowY: "scroll",
        }}
      >
        {props.children}
      </motion.div>
      </motion.div>
    </Form>
  );
}

const StyledButtonGroup = styled("div")(
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

function cycleExpansionState(expansionState: LeafCardExpansionState): LeafCardExpansionState {
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