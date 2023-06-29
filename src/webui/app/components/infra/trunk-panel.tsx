import { Container, styled, Toolbar } from "@mui/material";
import { useLocation } from "@remix-run/react";
import { AnimatePresence, motion } from "framer-motion";
import type { PropsWithChildren } from "react";
import { extractTrunkFromPath } from "~/rendering/routes";
import { useBigScreen } from "~/rendering/use-big-screen";

const SMALL_SCREEN_ANIMATION_START = "100vw";
const SMALL_SCREEN_ANIMATION_END = "100vw";

interface TrunkPanelProps {
  show: boolean;
}

export function TrunkPanel(props: PropsWithChildren<TrunkPanelProps>) {
  const isBigScreen = useBigScreen();
  const location = useLocation();

  return (
    <AnimatePresence mode="wait" initial={false}>
      {props.show && (
        <StyledMotionDrawer
          id="trunk-panel"
          key={extractTrunkFromPath(location.pathname)}
          initial={{
            opacity: 0,
            x: isBigScreen ? undefined : SMALL_SCREEN_ANIMATION_START,
          }}
          animate={{ opacity: 1, x: isBigScreen ? undefined : 0 }}
          exit={{
            opacity: 0,
            x: isBigScreen ? undefined : SMALL_SCREEN_ANIMATION_END,
          }}
          transition={{ duration: 0.2 }}
          isBigScreen={isBigScreen}
        >
          <Container maxWidth="lg" disableGutters>
            <Toolbar />
            {props.children}
          </Container>
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
    background-color: ${theme.palette.background.paper};

    &::-webkit-scrollbar {
      display: none;
    }
  `
);
