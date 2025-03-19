import { Card, CardActions } from "@mui/material";
import type { PropsWithChildren } from "react";

export function EntityActionHeader(props: PropsWithChildren) {
  return (
    <Card sx={{ marginTop: "1rem" }}>
      <CardActions>{props.children}</CardActions>
    </Card>
  );
}
