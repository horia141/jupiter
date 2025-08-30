import { Box } from "@mui/material";
import { AnimatePresence, motion } from "framer-motion";

import { useBigScreen } from "~/rendering/use-big-screen";

export interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const SMALL_SCREEN_INITIAL = { x: "100vw", opacity: 0 };
const BIG_SCREEN_INITIAL = { opacity: 0 };
const SMALL_SCREEN_ANIMATE = { x: 0, opacity: 1 };
const BIG_SCREEN_ANIMATE = { opacity: 1 };
const SMALL_SCREEN_EXIT = { x: "-100vw", opacity: 0 };
const BIG_SCREEN_EXIT = { opacity: 0 };

export function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  const isBigScreen = useBigScreen();

  return (
    <Box
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      sx={{ paddingTop: "0.25rem" }}
      {...other}
    >
      <AnimatePresence>
        {value === index && (
          <motion.div
            key={`tab-panel-${index}`}
            initial={isBigScreen ? BIG_SCREEN_INITIAL : SMALL_SCREEN_INITIAL}
            animate={isBigScreen ? BIG_SCREEN_ANIMATE : SMALL_SCREEN_ANIMATE}
            exit={isBigScreen ? BIG_SCREEN_EXIT : SMALL_SCREEN_EXIT}
            transition={{ duration: 0.2 }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </Box>
  );
}
