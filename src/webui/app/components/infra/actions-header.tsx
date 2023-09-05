import CloseIcon from "@mui/icons-material/Close";
import { Box, IconButton, styled } from "@mui/material";
import { Link } from "@remix-run/react";
import type { PropsWithChildren } from "react";

interface ActionHeaderProps {
  returnLocation: string;
}

export function ActionHeader(props: PropsWithChildren<ActionHeaderProps>) {
  return (
    <OuterWrapper>
      <InnerWrapper>{props.children}</InnerWrapper>
      <IconButton sx={{ marginLeft: "auto" }}>
        <Link to={props.returnLocation} preventScrollReset>
          <CloseIcon />
        </Link>
      </IconButton>
    </OuterWrapper>
  );
}

const OuterWrapper = styled(Box)(({ theme }) => ({
  display: "flex",
  flexDirection: "row",
  gap: "1rem",
  paddingTop: "1rem",
}));

const InnerWrapper = styled(Box)(({ theme }) => ({
  display: "flex",
  flexDirection: "row",
  gap: "1rem",
  flexWrap: "wrap",
}));
