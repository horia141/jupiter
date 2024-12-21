import { Container } from "@mui/material";
import type { PropsWithChildren } from "react";

export function StandaloneContainer(props: PropsWithChildren) {
  return (
    <Container maxWidth="sm" sx={{ paddingTop: "1rem" }}>
      {props.children}
    </Container>
  );
}
