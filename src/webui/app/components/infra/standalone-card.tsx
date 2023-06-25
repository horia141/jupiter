import { Container } from "@mui/material";
import type { PropsWithChildren } from "react";

export function StandaloneCard(props: PropsWithChildren) {
  return (
    <Container maxWidth="sm" sx={{ paddingTop: "1rem" }}>
      {props.children}
    </Container>
  );
}
