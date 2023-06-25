import { ButtonGroup, Card, CardActions } from "@mui/material";
import type { PropsWithChildren } from "react";

export function EntityActionHeader(props: PropsWithChildren) {
  return (
    <Card sx={{ marginTop: "1rem" }}>
      <CardActions>
        <ButtonGroup>{props.children}</ButtonGroup>
      </CardActions>
    </Card>
  );
}
