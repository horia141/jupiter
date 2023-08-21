import { Settings } from "@mui/icons-material";
import Logout from "@mui/icons-material/Logout";
import MenuIcon from "@mui/icons-material/Menu";
import {
  Alert,
  AlertTitle,
  AppBar,
  Avatar,
  Badge,
  Box,
  Button,
  ButtonGroup,
  Divider,
  IconButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Toolbar,
  Typography,
} from "@mui/material";
import type { LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import { Form, Link, ShouldRevalidateFunction, useCatch, useOutlet } from "@remix-run/react";
import Sidebar from "~/components/sidebar";

import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import CardMembershipIcon from "@mui/icons-material/CardMembership";
import SecurityIcon from "@mui/icons-material/Security";
import SportsEsportsIcon from "@mui/icons-material/SportsEsports";
import { UserFeature } from "jupiter-gen";
import { useContext, useState } from "react";
import { getLoggedInApiClient } from "~/api-clients";
import { DocsHelp, DocsHelpSubject } from "~/components/docs-help";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import { TrunkPanel } from "~/components/infra/trunk-panel";
import ProgressReporter from "~/components/progress-reporter";
import SearchBox from "~/components/search-box";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { isUserFeatureAvailable } from "~/logic/domain/user";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { useRootNeedsToShowTrunk } from "~/rendering/use-nested-entities";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";
import { ScoreSnackbarManager } from "~/components/gamification/score-snackbar-manager";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";

// @secureFn
export async function loader({ request }: LoaderArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  const client = getLoggedInApiClient(session);
  const response = await client.loadTopLevelInfo.loadTopLevelInfo({});

  if (!response.user || !response.workspace) {
    return redirect("/init");
  }

  const progressReporterTokenResponse =
    await client.loadProgressReporterToken.loadProgressReporterToken({});

  return json({
    userFeatureFlagControls: response.user_feature_flag_controls,
    workspaceFeatureFlagControls: response.workspace_feature_flag_controls,
    user: response.user,
    userScoreOverview: response.user_score_overview,
    workspace: response.workspace,
    progressReporterToken:
      progressReporterTokenResponse.progress_reporter_token_ext,
  });
}

export const shouldRevalidate: ShouldRevalidateFunction = standardShouldRevalidate;

// @secureFn
export default function Workspace() {
  const outlet = useOutlet();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const isBigScreen = useBigScreen();
  const shouldShowTrunk = useRootNeedsToShowTrunk();
  const [showSidebar, setShowSidebar] = useState(isBigScreen);

  const globalProperties = useContext(GlobalPropertiesContext);

  const [accountMenuAnchorEl, setAccountMenuAnchorEl] =
    useState<null | HTMLElement>(null);
  const accountMenuOpen = Boolean(accountMenuAnchorEl);
  const handleAccountMenuClick = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    setAccountMenuAnchorEl(event.currentTarget);
  };
  const handleAccountMenuClose = () => {
    setAccountMenuAnchorEl(null);
  };

  const topLevelInfo = {
    userFeatureFlagControls: loaderData.userFeatureFlagControls,
    workspaceFeatureFlagControls: loaderData.workspaceFeatureFlagControls,
    user: loaderData.user,
    userScoreOverview: loaderData.userScoreOverview,
    workspace: loaderData.workspace,
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column" }}>
      <AppBar
        position="fixed"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
      >
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            onClick={() => setShowSidebar((s) => !s)}
          >
            <MenuIcon />
          </IconButton>

          <Typography
            noWrap
            variant="h6"
            component="div"
            sx={{ flexGrow: 1, display: { xs: "none", sm: "block" } }}
          >
            Jupiter
          </Typography>

          <SearchBox />

          <ProgressReporter token={loaderData.progressReporterToken} />

          <DocsHelp size="medium" subject={DocsHelpSubject.ROOT} />

          <IconButton
            onClick={handleAccountMenuClick}
            size="large"
            color="inherit"
          >
            <Badge
              badgeContent={loaderData.userScoreOverview?.daily_score}
              color="success"
            >
              <Avatar
                sx={{ width: "1.75rem", height: "1.75rem" }}
                alt={loaderData.user.name.the_name}
                src={loaderData.user.avatar.avatar_as_data_url}
              />
            </Badge>
          </IconButton>

          <Menu
            id="basic-menu"
            anchorEl={accountMenuAnchorEl}
            open={accountMenuOpen}
            onClose={handleAccountMenuClose}
            MenuListProps={{
              "aria-labelledby": "basic-button",
            }}
          >
            {isUserFeatureAvailable(
              loaderData.user,
              UserFeature.GAMIFICATION
            ) && (
              <MenuItem
                to="/workspace/gamification"
                component={Link}
                onClick={handleAccountMenuClose}
              >
                <ListItemIcon>
                  <SportsEsportsIcon />
                </ListItemIcon>
                <ListItemText>
                  Today: {loaderData.userScoreOverview?.daily_score}
                  <Divider orientation="vertical" flexItem />
                  Week: {loaderData.userScoreOverview?.weekly_score}
                </ListItemText>
                <Divider />
              </MenuItem>
            )}
            <MenuItem
              to="/workspace/account"
              component={Link}
              onClick={handleAccountMenuClose}
            >
              <ListItemIcon>
                <AccountCircleIcon />
              </ListItemIcon>
              <ListItemText>Account</ListItemText>
            </MenuItem>
            <MenuItem
              to="/workspace/security"
              component={Link}
              onClick={handleAccountMenuClose}
            >
              <ListItemIcon>
                <SecurityIcon />
              </ListItemIcon>
              <ListItemText>Security</ListItemText>
            </MenuItem>
            <MenuItem
              to="/workspace/settings"
              component={Link}
              onClick={handleAccountMenuClose}
            >
              <ListItemIcon>
                <Settings />
              </ListItemIcon>
              <ListItemText>Settings</ListItemText>
            </MenuItem>
            <MenuItem
              to="/workspace/subscription"
              component={Link}
              onClick={handleAccountMenuClose}
            >
              <ListItemIcon>
                <CardMembershipIcon />
              </ListItemIcon>
              <ListItemText>Subscription</ListItemText>
            </MenuItem>
            <Divider />
            <Form method="post" action="/logout">
              <MenuItem type="submit" component="button">
                <ListItemIcon>
                  <Logout />
                </ListItemIcon>
                <ListItemText>Logout</ListItemText>
              </MenuItem>
            </Form>
          </Menu>
        </Toolbar>
      </AppBar>

      <Sidebar
        showSidebar={showSidebar}
        topLevelInfo={topLevelInfo}
        onClickForNavigation={() => {
          if (isBigScreen) return;
          setShowSidebar(false);
        }}
      />

      <TopLevelInfoContext.Provider value={topLevelInfo}>
        <TrunkPanel show={shouldShowTrunk}>{outlet}</TrunkPanel>
      </TopLevelInfoContext.Provider>

      <ScoreSnackbarManager />
    </Box>
  );
}

export function CatchBoundary() {
  const caught = useCatch();

  if (caught.status === 426 /* UPGRADE REQUIRED */) {
    return (
      <Alert severity="warning">
        <AlertTitle>Your session has expired! Login again!</AlertTitle>
        <ButtonGroup>
          <Button variant="outlined" component={Link} to="/login">
            Login
          </Button>
        </ButtonGroup>
      </Alert>
    );
  }

  throw new Error(`Unhandled error: ${caught.status}`);
}

export const ErrorBoundary = makeErrorBoundary(
  () => `There was an error loading the workspace! Please try again!`
);
