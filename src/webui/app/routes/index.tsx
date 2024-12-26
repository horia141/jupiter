import { Button, ButtonGroup, Typography } from "@mui/material";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link } from "@remix-run/react";
import { useContext } from "react";
import { LifecyclePanel } from "~/components/infra/layout/lifecycle-panel";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { SmartAppBar } from "~/components/infra/smart-appbar";
import { Logo } from "~/components/logo";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Index() {
  const globalProperties = useContext(GlobalPropertiesContext);

  return (
    <StandaloneContainer>
      <SmartAppBar>
        <Logo />
        <Typography
          noWrap
          variant="h6"
          component="div"
          sx={{ flexGrow: 1, display: { xs: "none", sm: "block" } }}
        >
          {globalProperties.title}
        </Typography>
      </SmartAppBar>

      <LifecyclePanel>
        <ButtonGroup>
          <Button variant="contained" to="/workspace" component={Link}>
            Go To The Workspace
          </Button>

          <Button
            variant="outlined"
            to={globalProperties.docsUrl}
            component={Link}
          >
            Go To The Docs
          </Button>
        </ButtonGroup>
      </LifecyclePanel>
    </StandaloneContainer>
  );
}
