import { Settings } from "@mui/icons-material";
import Logout from "@mui/icons-material/Logout";
import MenuIcon from "@mui/icons-material/Menu";
import {
  Alert,
  AlertTitle,
  AppBar,
  Avatar,
  Badge,
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
import type { LinksFunction, LoaderArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Form, Link, useCatch, useOutlet } from "@remix-run/react";
import Sidebar from "~/components/sidebar";

import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import CardMembershipIcon from "@mui/icons-material/CardMembership";
import SecurityIcon from "@mui/icons-material/Security";
import SportsEsportsIcon from "@mui/icons-material/SportsEsports";
import { AnimatePresence, useAnimate } from "framer-motion";
import { UserFeature } from "@jupiter/webapi-client";
import { useContext, useEffect, useState } from "react";
import { getLoggedInApiClient } from "~/api-clients";
import { DocsHelp, DocsHelpSubject } from "~/components/docs-help";
import {
  ScoreSnackbarManager,
  useScoreActionSingleton,
} from "~/components/gamification/score-snackbar-manager";
import { makeErrorBoundary } from "~/components/infra/error-boundary";
import ProgressReporter from "~/components/progress-reporter";
import SearchBox from "~/components/search-box";
import { isUserFeatureAvailable } from "~/logic/domain/user";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import { getSession } from "~/sessions";
import { TopLevelInfoContext } from "~/top-level-context";

import { WorkspaceContainer } from "~/components/infra/layout/workspace-container";
import { GlobalPropertiesContext } from "~/global-properties-client";
import editorJsTweaks from "~/styles/editorjs-tweaks.css";

export const links: LinksFunction = () => [
  { rel: "stylesheet", href: editorJsTweaks },
];

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

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

// @secureFn
export default function Workspace() {
  const outlet = useOutlet();
  const loaderData = useLoaderDataSafeForAnimation<typeof loader>();
  const isBigScreen = useBigScreen();
  const [showSidebar, setShowSidebar] = useState(isBigScreen);
  const scoreAction = useScoreActionSingleton();
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

  const [badgeRef, animateBadge] = useAnimate();

  useEffect(() => {
    if (!scoreAction) return;
    animateBadge(badgeRef.current, { scale: 1.2 }, { duration: 0.15 }).then(
      () => {
        animateBadge(badgeRef.current, { scale: 1 }, { duration: 0.15 });
      }
    );
  }, [animateBadge, badgeRef, scoreAction]);

  // Checkout https://css-tricks.com/the-trick-to-viewport-units-on-mobile/
  // for reasoning.
  function updateOurOwnVh() {
    // First we get the viewport height and we multiple it by 1% to get a value for a vh unit
    const vh = window.innerHeight * 0.01;
    // Then we set the value in the --vh custom property to the root of the document
    document.documentElement.style.setProperty("--vh", `${vh}px`);
  }

  useEffect(() => {
    updateOurOwnVh();
    // We listen to the resize event
    window.addEventListener("resize", updateOurOwnVh);
    return () => {
      window.removeEventListener("resize", updateOurOwnVh);
    };
  }, []);

  const topLevelInfo = {
    userFeatureFlagControls: loaderData.userFeatureFlagControls,
    workspaceFeatureFlagControls: loaderData.workspaceFeatureFlagControls,
    user: loaderData.user,
    userScoreOverview: loaderData.userScoreOverview,
    workspace: loaderData.workspace,
  };

  return (
    <TopLevelInfoContext.Provider value={topLevelInfo}>
      <WorkspaceContainer>
        <AppBar
          position="static"
          sx={{ zIndex: (theme) => theme.zIndex.drawer + 10 }}
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
              {globalProperties.title}
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
                ref={badgeRef}
                badgeContent={
                  scoreAction
                    ? scoreAction.daily_total_score
                    : loaderData.userScoreOverview?.daily_score.total_score
                }
                color="success"
              >
                <Avatar
                  sx={{ width: "1.75rem", height: "1.75rem" }}
                  alt={loaderData.user.name}
                  src={loaderData.user.avatar}
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
                    Today:{" "}
                    {scoreAction
                      ? scoreAction.daily_total_score
                      : loaderData.userScoreOverview?.daily_score.total_score}
                    <Divider orientation="vertical" flexItem />
                    Week:{" "}
                    {scoreAction
                      ? scoreAction.weekly_total_score
                      : loaderData.userScoreOverview?.weekly_score.total_score}
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

        <AnimatePresence mode="wait" initial={false}>
          {outlet}
        </AnimatePresence>

        <ScoreSnackbarManager scoreAction={scoreAction} />
      </WorkspaceContainer>
    </TopLevelInfoContext.Provider>
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
