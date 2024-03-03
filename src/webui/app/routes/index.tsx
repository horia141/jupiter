import { Button, ButtonGroup } from "@mui/material";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { Link } from "@remix-run/react";
import { useContext } from "react";
import { StandaloneContainer } from "~/components/infra/layout/standalone-container";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Index() {
  const globalProperties = useContext(GlobalPropertiesContext);

  return (
    <StandaloneContainer>
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
    </StandaloneContainer>
  );
}
