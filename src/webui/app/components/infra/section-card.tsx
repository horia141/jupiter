import type { CardProps, ChipProps } from "@mui/material";
import { Card, CardContent, Chip, styled } from "@mui/material";
import type { PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";
import { ExtraControls } from "./layout/extra-controls";

interface SectionCardProps {
  title: string;
  actions?: JSX.Element[];
}

export function SectionCard(props: PropsWithChildren<SectionCardProps>) {
  const isBigScreen = useBigScreen();

  return (
    <StyledCard>
      <SectionHeader>
        <SectionTitle label={props.title} />
        {props.actions && (
          <ExtraControls isBigScreen={isBigScreen} controls={props.actions} />
        )}
      </SectionHeader>
      <CardContent>{props.children}</CardContent>
    </StyledCard>
  );
}

const SectionHeader = styled("div")(({ theme }) => ({
  display: "flex",
  flexWrap: "nowrap",
  justifyContent: "space-between",
  alignItems: "stretch",
  height: "3rem",
}));

const StyledCard = styled(Card)<CardProps>(({ theme }) => ({
  position: "relative",
}));

const SectionTitle = styled(Chip)<ChipProps>(({ theme }) => ({
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