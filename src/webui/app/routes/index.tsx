import { Button, Container } from "@mui/material";
import { Link } from "@remix-run/react";

export default function Index() {
  return (
    <Container maxWidth="lg">
      <Button variant="outlined" to="/workspace" component={Link}>
        Go To The Workspace
      </Button>
    </Container>
  );
}
