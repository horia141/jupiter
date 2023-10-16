import { Toolbar, useTheme } from "@mui/material";
import { useLocation } from "@remix-run/react";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useLayoutEffect } from "react";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import DeleteIcon from "@mui/icons-material/Delete";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import { Box, ButtonGroup, IconButton, styled } from "@mui/material";
import { Form, Link, useNavigate } from "@remix-run/react";
import type { PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";

const BIG_SCREEN_WIDTH = "480px";
const BIG_SCREEN_ANIMATION_START = "480px";
const BIG_SCREEN_ANIMATION_END = "480px";
const SMALL_SCREEN_WIDTH = "100%";
const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

interface SideCardProps {
  showArchiveButton?: boolean;
  enableArchiveButton?: boolean;
  returnLocation: string;
}

export function SideCard(props: PropsWithChildren<SideCardProps>) {
  const isBigScreen = useBigScreen();
  const navigation = useNavigate();
  const location = useLocation();

  const containerRef = useRef<HTMLDivElement>(null);

  function handleScroll(ref: HTMLDivElement, pathname: string) {
      console.log(isBigScreen, window.location.pathname, location.pathname, pathname, ref.scrollTop);
    window.sessionStorage.setItem(`scroll:${pathname}`, `${ref.scrollTop}`);
  }

  useEffect(() => {
    if (containerRef.current === null) {
      return;
    }

    function handleScrollSpecial() {
      handleScroll(containerRef.current!, location.pathname);
    }

      containerRef.current.scrollTo(
        0,
        parseInt(
          window.sessionStorage.getItem(`scroll:${location.pathname}`) ?? "0"
        )
      );
      containerRef.current.addEventListener("scrollend", handleScrollSpecial);

    return () => {
      containerRef.current?.removeEventListener("scrollend", handleScrollSpecial);
    };
  }, [containerRef, location]);

  return (
    <Form method="post">
      <StyledButtonGroup isBigScreen={isBigScreen}>
        <ButtonGroup size="small">
          <IconButton>
            <Link to={props.returnLocation}>
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
      <Box
      ref={containerRef}
           
        style={{ padding: "0.5rem ", height: `calc(100vh - 4rem - ${isBigScreen ? "4rem" : "3.5rem"})`, overflowY: "scroll"}}>{props.children}</Box>
    </Form>
  );
}

interface StyledButtionGroupProps {
  isBigScreen: boolean;
}

const StyledButtonGroup = styled("div")<StyledButtionGroupProps>(
  ({ theme, isBigScreen }) => `
    display: flex;
    width: 100%;
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


interface SidePanelProps {
  show: boolean;
}

export function SidePanel(props: PropsWithChildren<SidePanelProps>) {
  const isBigScreen = useBigScreen();
  const location = useLocation();

  return (
    <AnimatePresence mode="wait" initial={false}>
      {props.show && (
        <StyledMotionDrawer
          id="side-panel"
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
    background-color: ${theme.palette.background.paper};
    border-left: 1px solid rgba(0, 0, 0, 0.12);
  `
);
