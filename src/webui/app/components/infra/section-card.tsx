import { Card, CardActions, CardContent, Chip, styled } from "@mui/material";
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
}

export function SectionCard(props: PropsWithChildren<SectionCardProps>) {
  const actionsPosition = props.actionsPosition ?? ActionsPosition.ABOVE;

  return (
    <StyledCard id={props.id}>
      <Form method="post">
        <SectionHeader>
          <SectionTitle label={props.title} />
          {actionsPosition === ActionsPosition.ABOVE && props.actions}
        </SectionHeader>
        <CardContent>{props.children}</CardContent>
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
  alignItems: "stretch",
  height: "3rem",
}));

const StyledCard = styled(Card)(() => ({
  position: "relative",
}));

const SectionTitle = styled(Chip)(() => ({
  position: "relative",
  maxWidth: "calc(100% - 5rem)",
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
