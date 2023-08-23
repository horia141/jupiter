import { Button, ButtonGroup, Container } from "@mui/material";
import { Link, ShouldRevalidateFunction } from "@remix-run/react";
import { useContext } from "react";
import { GlobalPropertiesContext } from "~/global-properties-client";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;

export default function Index() {
  const globalProperties = useContext(GlobalPropertiesContext);

  return (
    <Container maxWidth="lg">
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
    </Container>
  );
}
