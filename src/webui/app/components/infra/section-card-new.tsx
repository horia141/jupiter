import { Card, CardContent, Chip, styled } from "@mui/material";
import type { PropsWithChildren } from "react";

interface SectionCardNewProps {
  id?: string;
  title: string;
  actions?: JSX.Element;
}

export function SectionCardNew(props: PropsWithChildren<SectionCardNewProps>) {
  return (
    <StyledCard id={props.id}>
      <SectionHeader>
        <SectionTitle label={props.title} />
        {props.actions}
      </SectionHeader>
      <CardContent>{props.children}</CardContent>
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
