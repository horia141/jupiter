import { UserFeature } from "@jupiter/webapi-client";
import { Settings } from "@mui/icons-material";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import Logout from "@mui/icons-material/Logout";
import MenuIcon from "@mui/icons-material/Menu";
import PolicyIcon from "@mui/icons-material/Policy";
import SecurityIcon from "@mui/icons-material/Security";
import SportsEsportsIcon from "@mui/icons-material/SportsEsports";
import {
  Alert,
  AlertTitle,
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
} from "@mui/material";
import type { LinksFunction, LoaderFunctionArgs } from "@remix-run/node";
import { json, redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Form, Link, useOutlet } from "@remix-run/react";
import { AnimatePresence, useAnimate } from "framer-motion";
import { useContext, useEffect, useState } from "react";
import { getLoggedInApiClient } from "~/api-clients.server";
import { CommunityLink } from "~/components/community-link";
import { DocsHelp, DocsHelpSubject } from "~/components/docs-help";
import {
  ScoreSnackbarManager,
  useScoreActionSingleton,
} from "~/components/gamification/score-snackbar-manager";
import { makeRootErrorBoundary } from "~/components/infra/error-boundary";
import { WorkspaceContainer } from "~/components/infra/layout/workspace-container";
import { SmartAppBar } from "~/components/infra/smart-appbar";
import { ReleaseUpdateWidget } from "~/components/release-update-widget";
import SearchBox from "~/components/search-box";
import Sidebar from "~/components/sidebar";
import { Title } from "~/components/title";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { isUserFeatureAvailable } from "~/logic/domain/user";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { useBigScreen } from "~/rendering/use-big-screen";
import { useLoaderDataSafeForAnimation } from "~/rendering/use-loader-data-for-animation";
import editorJsTweaks from "~/styles/editorjs-tweaks.css";
import { TopLevelInfoContext } from "~/top-level-context";

export const links: LinksFunction = () => [
  { rel: "stylesheet", href: editorJsTweaks },
];

// @secureFn
export async function loader({ request }: LoaderFunctionArgs) {
  const apiClient = await getLoggedInApiClient(request);
  const response = await apiClient.loadTopLevelInfo.loadTopLevelInfo({});

  if (!response.user || !response.workspace) {
    return redirect("/app/init");
  }

  const progressReporterTokenResponse =
    await apiClient.loadProgressReporterToken.loadProgressReporterToken({});

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
    event: React.MouseEvent<HTMLButtonElement>,
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
      },
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
        <SmartAppBar>
          <IconButton
            id="show-sidebar"
            size="large"
            edge="start"
            color="inherit"
            onClick={() => setShowSidebar((s) => !s)}
          >
            <MenuIcon />
          </IconButton>

          <Title hideOnSmallScreen />

          <SearchBox />

          {/* <ProgressReporter token={loaderData.progressReporterToken} /> */}

          <CommunityLink />

          <DocsHelp size="medium" subject={DocsHelpSubject.ROOT} />

          <IconButton
            id="account-menu"
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
              UserFeature.GAMIFICATION,
            ) && (
              <MenuItem
                to="/app/workspace/gamification"
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
              id="account"
              to="/app/workspace/account"
              component={Link}
              onClick={handleAccountMenuClose}
            >
              <ListItemIcon>
                <AccountCircleIcon />
              </ListItemIcon>
              <ListItemText>Account</ListItemText>
            </MenuItem>
            <MenuItem
              id="security"
              to="/app/workspace/security"
              component={Link}
              onClick={handleAccountMenuClose}
            >
              <ListItemIcon>
                <SecurityIcon />
              </ListItemIcon>
              <ListItemText>Security</ListItemText>
            </MenuItem>
            <MenuItem
              id="settings"
              to="/app/workspace/settings"
              component={Link}
              onClick={handleAccountMenuClose}
            >
              <ListItemIcon>
                <Settings />
              </ListItemIcon>
              <ListItemText>Settings</ListItemText>
            </MenuItem>
            <Divider />
            <MenuItem
              component={"a"}
              href={globalProperties.termsOfServiceUrl}
              target="_blank"
            >
              <ListItemIcon>
                <PolicyIcon />
              </ListItemIcon>
              <ListItemText>Terms of Service</ListItemText>
            </MenuItem>
            <MenuItem
              component={"a"}
              href={globalProperties.privacyPolicyUrl}
              target="_blank"
            >
              <ListItemIcon>
                <PolicyIcon />
              </ListItemIcon>
              <ListItemText>Privacy Policy</ListItemText>
            </MenuItem>
            <Divider />
            <Form method="post" action="/app/logout">
              <MenuItem id="logout" type="submit" component="button">
                <ListItemIcon>
                  <Logout />
                </ListItemIcon>
                <ListItemText>Logout</ListItemText>
              </MenuItem>
            </Form>
          </Menu>
        </SmartAppBar>

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
        <ReleaseUpdateWidget />
      </WorkspaceContainer>
    </TopLevelInfoContext.Provider>
  );
}

export const ErrorBoundary = makeRootErrorBoundary({
  error: () => `There was an error loading the workspace! Please try again!`,
});
