import AddIcon from "@mui/icons-material/Add";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import CloseIcon from "@mui/icons-material/Close";
import { Button, ButtonGroup, IconButton, styled } from "@mui/material";
import { Link, useLocation } from "@remix-run/react";
import { motion, useIsPresent } from "framer-motion";
import { useEffect, useRef, type PropsWithChildren } from "react";
import { useHydrated } from "remix-utils";
import { extractBranchFromPath } from "~/rendering/routes";
import {
  restoreScrollPosition,
  saveScrollPosition,
} from "~/rendering/scroll-restoration";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useTrunkNeedsToShowLeaf } from "~/rendering/use-nested-entities";

const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

interface BranchPanelProps {
  createLocation?: string;
  extraFilters?: JSX.Element;
  returnLocation: string;
}

export function BranchPanel(props: PropsWithChildren<BranchPanelProps>) {
  const location = useLocation();
  const isBigScreen = useBigScreen();
  const containerRef = useRef<HTMLDivElement>(null);
  const isPresent = useIsPresent();
  const isHydrated = useHydrated();
  const shouldShowALeaf = useTrunkNeedsToShowLeaf();

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
        extractBranchFromPath(location.pathname)
      );
    }

    restoreScrollPosition(
      containerRef.current,
      extractBranchFromPath(location.pathname)
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
    <BranchPanelFrame
      id="branch-panel"
      key={extractBranchFromPath(location.pathname)}
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
      {(isBigScreen || !shouldShowALeaf) && (
        <BranchPanelControls id="branch-panel-controls">
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

          {props.extraFilters}

          <IconButton sx={{ marginLeft: "auto" }}>
            <Link to={props.returnLocation}>
              <CloseIcon />
            </Link>
          </IconButton>
        </BranchPanelControls>
      )}

      <BranchPanelContent
        id="branch-panel-content"
        ref={containerRef}
        isbigscreen={isBigScreen ? "true" : "false"}
        hasleaf={shouldShowALeaf ? "true" : "false"}
      >
        {props.children}
      </BranchPanelContent>
    </BranchPanelFrame>
  );
}

interface BranchPanelFrameProps {
  isBigScreen: boolean;
}

const BranchPanelFrame = styled(motion.div)<BranchPanelFrameProps>(
  ({ theme, isBigScreen }) => ({
    backgroundColor: theme.palette.background.paper,
  })
);

const BranchPanelControls = styled("div")(
  ({ theme }) => `
      display: flex;
      align-items: center;
      gap: 1rem;
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

interface BranchPanelContentProps {
  isbigscreen: string;
  hasleaf: string;
}

const BranchPanelContent = styled("div")<BranchPanelContentProps>(
  ({ isbigscreen, hasleaf }) => ({
    padding: isbigscreen === "true" ? "0.5rem" : "0px",
    height: `calc(var(--vh, 1vh) * 100 - ${
      isbigscreen === "true" ? "4rem" : "3.5rem"
    } - ${
      isbigscreen === "true" ? "4rem" : hasleaf === "false" ? "3.5rem" : "0px"
    })`,
    overflowY: "scroll",
  })
);
