import { Button, ButtonGroup } from "@mui/material";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link } from "@remix-run/react";
import { useContext } from "react";

import { CommunityLink } from "~/components/infra/community-link";
import { DocsHelp, DocsHelpSubject } from "~/components/infra/docs-help";
import { LifecyclePanel } from "~/components/infra/layout/lifecycle-panel";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { SmartAppBar } from "~/components/infra/smart-appbar";
import { Logo } from "~/components/infra/logo";
import { Title } from "~/components/infra/title";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";

export const shouldRevalidate: ShouldRevalidateFunction = () => false;

export default function Index() {
  const globalProperties = useContext(GlobalPropertiesContext);

  return (
    <StandaloneContainer>
      <SmartAppBar>
        <Logo />
        <Title />

        <CommunityLink />

        <DocsHelp size="medium" subject={DocsHelpSubject.ROOT} />
      </SmartAppBar>

      <LifecyclePanel>
        <ButtonGroup>
          <Button variant="contained" to="/app/workspace" component={Link}>
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
