import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import { ButtonGroup, IconButton, styled } from "@mui/material";
import { Form, Link, useLocation, useNavigate } from "@remix-run/react";
import { motion } from "framer-motion";
import type { PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";

const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

interface ToolPanelProps {
  method?: "get" | "post";
  returnLocation: string;
}

export function ToolPanel2(props: PropsWithChildren<ToolPanelProps>) {
  const isBigScreen = useBigScreen();
  const location = useLocation();
  const navigation = useNavigate();

  return (
    <ToolPanelFrame
      id="tool-panel"
      isBigScreen={isBigScreen}
      key={location.pathname}
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
      {!isBigScreen && (
        <ToolPanelControls id="tool-panel-controls">
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
        </ToolPanelControls>
      )}
      <ToolCardContent
        isbigscreen={isBigScreen ? "true" : "false"}
        method={props.method || "post"}
      >
        {props.children}
      </ToolCardContent>
    </ToolPanelFrame>
  );
}

interface ToolPanelFrameProps {
  isBigScreen: boolean;
}

const ToolPanelFrame = styled(motion.div)<ToolPanelFrameProps>(
  ({ theme, isBigScreen }) => ({})
);

const ToolPanelControls = styled("div")(
  ({ theme }) => `
    display: flex;
    width: 100%;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    margin-bottom: 1rem;
    position: sticky;
    background-color: ${theme.palette.background.paper};
    z-index: ${theme.zIndex.drawer + 1};
    border-radius: 0px;
    box-shadow: 0px 5px 5px rgba(0, 0, 0, 0.2);
    `
);

interface ToolCardContentProps {
  isbigscreen: string;
}

const ToolCardContent = styled(Form)<ToolCardContentProps>(
  ({ isbigscreen }) => ({
    padding: "0.5rem",
    height: `calc(100vh - 4rem - ${
      isbigscreen === "true" ? "4rem" : "3.5rem"
    })`,
    overflowY: "scroll",
  })
);
