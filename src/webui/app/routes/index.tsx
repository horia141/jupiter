import { Button, ButtonGroup, Container } from "@mui/material";
import { Link } from "@remix-run/react";
import { useContext } from "react";
import { GlobalPropertiesContext } from "~/global-properties-client";

export default function Index() {
  const globalProperties = useContext(GlobalPropertiesContext);

  return (
    <Container maxWidth="lg">
      <ButtonGroup>
      <Button variant="contained" to="/workspace" component={Link}>
        Go To The Workspace
      </Button>

      <Button variant="outlined" to={globalProperties.docsUrl} component={Link}>
        Go To The Docs
      </Button>
      </ButtonGroup>
    </Container>
  );
}
