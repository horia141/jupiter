import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import DeleteIcon from "@mui/icons-material/Delete";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import { Box, ButtonGroup, IconButton, styled } from "@mui/material";
import { Form, Link, useLocation, useNavigate } from "@remix-run/react";
import SwitchRightIcon from '@mui/icons-material/SwitchRight';
import SwitchLeftIcon from '@mui/icons-material/SwitchLeft';
import { MotionConfig, motion, useIsPresent } from "framer-motion";
import { useEffect, useRef, type PropsWithChildren, useState } from "react";
import {
  restoreScrollPosition,
  saveScrollPosition,
} from "~/rendering/scroll-restoration";
import { useBigScreen } from "~/rendering/use-big-screen";

const BIG_SCREEN_WIDTH_STANDARD = "480px";
const BIG_SCREEN_WIDTH_EXPANDED = "calc(min(720px, 60vw))";
const SMALL_SCREEN_WIDTH = "100%";

interface LeafCardProps {
  showArchiveButton?: boolean;
  enableArchiveButton?: boolean;
  returnLocation: string;
  startExpanded?: boolean;
}

export function LeafCard(props: PropsWithChildren<LeafCardProps>) {
  const isBigScreen = useBigScreen();
  const navigation = useNavigate();
  const location = useLocation();
  const containerRef = useRef<HTMLDivElement>(null);
  const isPresent = useIsPresent();
  const [isExpanded, setIsExpanded] = useState(props.startExpanded ?? false);

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

  const containerVariants = {
    standard: {
      width: BIG_SCREEN_WIDTH_STANDARD
    },
    expanded: {
      width: BIG_SCREEN_WIDTH_EXPANDED
    },
    smallScreen: {
      width: SMALL_SCREEN_WIDTH
    }
  };

  return (
    <Form method="post">
      <StyledButtonGroup>
        <ButtonGroup size="small">
          {isBigScreen && <IconButton onClick={() => setIsExpanded((e) => !e)}>
              {isExpanded ? <SwitchLeftIcon /> : <SwitchRightIcon />}
          </IconButton>}
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
      <motion.div
        ref={containerRef}
        animate={isBigScreen ? (isExpanded ? "expanded" : "standard") : "smallScreen"}
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
