import { useContext } from "react";
import { WorkspaceFeature } from "@jupiter/webapi-client";
import { Settings } from "@mui/icons-material";
import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  styled,
} from "@mui/material";
import { Link } from "@remix-run/react";
import { AnimatePresence, motion } from "framer-motion";

import { isWorkspaceFeatureAvailable } from "~/logic/domain/workspace";
import { useBigScreen } from "~/rendering/use-big-screen";
import { TopLevelInfoContext } from "~/top-level-context";
import { StandardDivider } from "~/components/infra/standard-divider";

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
  const topLevelInfo = useContext(TopLevelInfoContext);

  console.log(topLevelInfo);

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
                to="/app/workspace"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>🏠</ListItemIcon>
                <ListItemText primary="Home" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/app/workspace/inbox-tasks"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>📥</ListItemIcon>
                <ListItemText primary="Inbox Tasks" />
              </ListItemButton>
            </ListItem>

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.WORKING_MEM,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/working-mem"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>🧠</ListItemIcon>
                  <ListItemText primary="Working Mem" />
                </ListItemButton>
              </ListItem>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.TIME_PLANS,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/time-plans"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>🏭</ListItemIcon>
                  <ListItemText primary="Time Plans" />
                </ListItemButton>
              </ListItem>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.SCHEDULE,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/calendar"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>📅</ListItemIcon>
                  <ListItemText primary="Calendar" />
                </ListItemButton>
              </ListItem>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.HABITS,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/habits"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>💪</ListItemIcon>
                  <ListItemText primary="Habits" />
                </ListItemButton>
              </ListItem>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.CHORES,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/chores"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>♻️</ListItemIcon>
                  <ListItemText primary="Chores" />
                </ListItemButton>
              </ListItem>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.BIG_PLANS,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/big-plans"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>🌍</ListItemIcon>
                  <ListItemText primary="Big Plans" />
                </ListItemButton>
              </ListItem>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.JOURNALS,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/journals"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>📓</ListItemIcon>
                  <ListItemText primary="Journals" />
                </ListItemButton>
              </ListItem>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.DOCS,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/docs"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>🗒️</ListItemIcon>
                  <ListItemText primary="Docs" />
                </ListItemButton>
              </ListItem>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.VACATIONS,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/vacations"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>🌴</ListItemIcon>
                  <ListItemText primary="Vacations" />
                </ListItemButton>
              </ListItem>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PROJECTS,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/projects"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>💡</ListItemIcon>
                  <ListItemText primary="Projects" />
                </ListItemButton>
              </ListItem>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.SMART_LISTS,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/smart-lists"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>🏛️</ListItemIcon>
                  <ListItemText primary="Smart Lists" />
                </ListItemButton>
              </ListItem>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.METRICS,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/metrics"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>📈</ListItemIcon>
                  <ListItemText primary="Metrics" />
                </ListItemButton>
              </ListItem>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.PERSONS,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/persons"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>👨</ListItemIcon>
                  <ListItemText primary="Persons" />
                </ListItemButton>
              </ListItem>
            )}

            {(isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.SLACK_TASKS,
            ) ||
              isWorkspaceFeatureAvailable(
                topLevelInfo.workspace,
                WorkspaceFeature.EMAIL_TASKS,
              )) && <StandardDivider title="Push Integrations" size="small" />}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.SLACK_TASKS,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/push-integrations/slack-tasks"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>💬</ListItemIcon>
                  <ListItemText primary="Slack Tasks" />
                </ListItemButton>
              </ListItem>
            )}

            {isWorkspaceFeatureAvailable(
              topLevelInfo.workspace,
              WorkspaceFeature.EMAIL_TASKS,
            ) && (
              <ListItem disablePadding>
                <ListItemButton
                  to="/app/workspace/push-integrations/email-tasks"
                  component={Link}
                  onClick={onClickNavigation}
                >
                  <ListItemIcon>📧</ListItemIcon>
                  <ListItemText primary="Email Tasks" />
                </ListItemButton>
              </ListItem>
            )}

            <StandardDivider title="Tools" size="small" />

            <ListItem disablePadding>
              <ListItemButton
                to="/app/workspace/tools/search"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>🔍</ListItemIcon>
                <ListItemText primary="Search" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/app/workspace/tools/report"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>📊</ListItemIcon>
                <ListItemText primary="Report" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/app/workspace/tools/pomodoro"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>🥫</ListItemIcon>
                <ListItemText primary="Pomodoro Timer" />
              </ListItemButton>
            </ListItem>

            <StandardDivider title="Process" size="small" />

            <ListItem disablePadding>
              <ListItemButton
                to="/app/workspace/tools/gen"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>🔮</ListItemIcon>
                <ListItemText primary="Generate Tasks" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/app/workspace/tools/gc"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>🗑</ListItemIcon>
                <ListItemText primary="Garbage Collect" />
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton
                to="/app/workspace/tools/stats"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>📊</ListItemIcon>
                <ListItemText primary="Compute Stats" />
              </ListItemButton>
            </ListItem>

            <StandardDivider title="Explore" size="small" />

            <ListItem disablePadding>
              <ListItemButton
                to="/app/workspace/settings"
                component={Link}
                onClick={onClickNavigation}
              >
                <ListItemIcon>
                  <Settings />
                </ListItemIcon>
                <ListItemText primary="More Features" />
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
    padding-top: env(safe-area-inset-top);
    height: 100%;
    overflow-x: auto;
    overflow-y: scroll;
    background-color: ${theme.palette.background.paper};
    border-right: 1px solid rgba(0, 0, 0, 0.12);

    &::-webkit-scrollbar {
      display: none;
    }
  `,
);
