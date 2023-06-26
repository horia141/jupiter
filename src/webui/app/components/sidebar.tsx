import {
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  styled,
  Toolbar,
} from "@mui/material";
import { Link } from "@remix-run/react";
import { AnimatePresence, motion } from "framer-motion";
import { useBigScreen } from "~/rendering/use-big-screen";

const BIG_SCREEN_WIDTH = "240px";
const BIG_SCREEN_ANIMATION_START = "-240px";
const BIG_SCREEN_ANIMATION_END = "0px";
const SMALL_SCREEN_WIDTH = "100%";
const SMALL_SCREEN_ANIMATION_START = "-100vw";
const SMALL_SCREEN_ANIMATION_END = "0vw";

interface SidebarProps {
  showSidebar: boolean;
  onClickForNavigation?: () => void;
}

export default function Sidebar(props: SidebarProps) {
  function onClickNavigation() {
    if (!props.onClickForNavigation) {
      return;
    }

    props.onClickForNavigation();
  }

  const isBigScreen = useBigScreen();

  return (
    <AnimatePresence>
      {props.showSidebar && (
        <StyledMotionDrawer
          initial={{
            x: isBigScreen
              ? BIG_SCREEN_ANIMATION_START
              : SMALL_SCREEN_ANIMATION_START,
          }}
          animate={{
            x: isBigScreen
              ? BIG_SCREEN_ANIMATION_END
              : SMALL_SCREEN_ANIMATION_END,
          }}
          exit={{
            x: isBigScreen
              ? BIG_SCREEN_ANIMATION_START
              : SMALL_SCREEN_ANIMATION_START,
          }}
          transition={{ type: "spring", bounce: 0.0, duration: 0.2 }}
          isBigScreen={isBigScreen}
        >
          <Toolbar />
          <List>
            <ListItem disablePadding>
              <ListItemButton
                to="/workspace"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>🏠</ListItemIcon>
                <ListItemText primary="Home" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/inbox-tasks"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>📥</ListItemIcon>
                <ListItemText primary="Inbox Tasks" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/habits"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>💪</ListItemIcon>
                <ListItemText primary="Habits" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/chores"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>♻️</ListItemIcon>
                <ListItemText primary="Chores" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/big-plans"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>🌍</ListItemIcon>
                <ListItemText primary="Big Plans" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/vacations"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>🌴</ListItemIcon>
                <ListItemText primary="Vacations" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/projects"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>💡</ListItemIcon>
                <ListItemText primary="Projects" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/smart-lists"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>🏛️</ListItemIcon>
                <ListItemText primary="Smart Lists" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/metrics"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>📈</ListItemIcon>
                <ListItemText primary="Metrics" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/persons"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>👨</ListItemIcon>
                <ListItemText primary="Persons" />
              </ListItemButton>
            </ListItem>

            <Divider textAlign="left">Push Integrations</Divider>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/push-integrations/slack-tasks"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>💬</ListItemIcon>
                <ListItemText primary="Slack Tasks" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/push-integrations/email-tasks"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>📧</ListItemIcon>
                <ListItemText primary="Email Tasks" />
              </ListItemButton>
            </ListItem>

            <Divider textAlign="left">Tools</Divider>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/tools/gen"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>🧰</ListItemIcon>
                <ListItemText primary="Generate Tasks" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/tools/report"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>🧰</ListItemIcon>
                <ListItemText primary="Report" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/workspace/tools/gc"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>🧰</ListItemIcon>
                <ListItemText primary="Garbage Collect" />
              </ListItemButton>
            </ListItem>
          </List>
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
    position: fixed;
    top: 0px;
    width: ${isBigScreen ? BIG_SCREEN_WIDTH : SMALL_SCREEN_WIDTH};
    z-index: ${theme.zIndex.drawer};
    height: 100%;
    overflow-x: auto;
    overflow-y: scroll;
    background-color: ${theme.palette.background.paper};
    border-right: 1px solid rgba(0, 0, 0, 0.12);

    &::-webkit-scrollbar {
      display: none;
    }
  `
);