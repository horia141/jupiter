import { Button, Container } from "@mui/material";
import { Link } from "@remix-run/react";
import { useContext } from "react";
import { GlobalPropertiesContext } from "~/global-properties-client";

export default function Index() {
  const globalProperties = useContext(GlobalPropertiesContext);
  
  return (
    <Container maxWidth="lg">
      <Button variant="outlined" to="/workspace" component={Link}>
        Go To The Workspace
      </Button>

      <Button variant="outlined" to={globalProperties.docsUrl} component={Link}>
        Go To The Docs
      </Button>
    </Container>
  );
}
