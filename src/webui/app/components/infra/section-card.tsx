import {
  Card,
  CardActions,
  CardContent,
  Chip,
  Stack,
  styled,
} from "@mui/material";
import { Form } from "@remix-run/react";
import type { PropsWithChildren } from "react";

export enum ActionsPosition {
  ABOVE,
  BELOW,
}

interface SectionCardProps {
  id?: string;
  title: string;
  actions?: JSX.Element;
  actionsPosition?: ActionsPosition;
  method?: "get" | "post";
}

export function SectionCard(props: PropsWithChildren<SectionCardProps>) {
  const actionsPosition = props.actionsPosition ?? ActionsPosition.ABOVE;

  return (
    <StyledCard id={props.id}>
      <Form method={props.method ?? "post"}>
        <SectionHeader>
          <SectionHeaderContent>
            <SectionTitle label={props.title} />
          </SectionHeaderContent>
          {actionsPosition === ActionsPosition.ABOVE && props.actions}
        </SectionHeader>
        <CardContent>
          <Stack spacing={2}>{props.children}</Stack>
        </CardContent>
        {actionsPosition === ActionsPosition.BELOW && (
          <CardActions>{props.actions}</CardActions>
        )}
      </Form>
    </StyledCard>
  );
}

const SectionHeader = styled("div")(() => ({
  display: "flex",
  flexWrap: "nowrap",
  justifyContent: "space-between",
  alignItems: "center",
  height: "3rem",
  width: "100%",
}));

const StyledCard = styled(Card)(() => ({
  position: "relative",
}));

const SectionHeaderContent = styled("div")(() => ({
  display: "flex",
  flex: "1 1 auto",
  minWidth: "0",
  flexWrap: "nowrap",
  justifyContent: "space-between",
  alignItems: "center",
  height: "3rem",
}));

const SectionTitle = styled(Chip)(() => ({
  position: "relative",
  top: "-0.05rem",
  fontSize: "1.5rem",
  fontVariant: "small-caps",
  height: "100%",
  left: "-0.05rem",
  paddingTop: "0.05rem",
  paddingBottom: "0.05rem",
  paddingRight: "2rem",
  paddingLeft: "0.5rem",
  borderRadius: "0px",
  borderBottomRightRadius: "4px",
}));
