import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import DeleteIcon from "@mui/icons-material/Delete";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import { Box, ButtonGroup, IconButton, styled } from "@mui/material";
import { Form, Link, useNavigate } from "@remix-run/react";
import type { PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";

interface LeafCardProps {
  showArchiveButton?: boolean;
  enableArchiveButton?: boolean;
  returnLocation: string;
}

export function LeafCard(props: PropsWithChildren<LeafCardProps>) {
  const isBigScreen = useBigScreen();
  const navigation = useNavigate();
  return (
    <Form method="post">
      <StyledButtonGroup isBigScreen={isBigScreen}>
        <ButtonGroup size="small">
          <IconButton>
            <Link to={props.returnLocation}>
              <KeyboardDoubleArrowRightIcon />
            </Link>
          </IconButton>
          <IconButton onClick={() => navigation(-1)}>
            <ArrowBackIcon />
          </IconButton>
        </ButtonGroup>

        {props.showArchiveButton && (
          <IconButton
            sx={{ marginLeft: "auto" }}
            disabled={!props.enableArchiveButton}
            type="submit"
            name="intent"
            value="archive"
          >
            <DeleteIcon />
          </IconButton>
        )}
      </StyledButtonGroup>
      <Box style={{ padding: "0.5rem " }}>{props.children}</Box>
    </Form>
  );
}

interface StyledButtionGroupProps {
  isBigScreen: boolean;
}

const StyledButtonGroup = styled("div")<StyledButtionGroupProps>(
  ({ theme, isBigScreen }) => `
    display: flex;
    width: 100%;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    margin-bottom: 1rem;
    position: sticky;
    top: ${isBigScreen ? "4rem" : "3.5rem"};
    background-color: ${theme.palette.background.paper};
    z-index: ${theme.zIndex.drawer + 1};
    border-radius: 0px;
    box-shadow: 0px 5px 5px rgba(0, 0, 0, 0.2);
    `
);
