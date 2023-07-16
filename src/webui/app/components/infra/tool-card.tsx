import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import { ButtonGroup, IconButton, Stack, styled } from "@mui/material";
import { Form, Link, useNavigate } from "@remix-run/react";
import type { PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";

interface ToolCardProps {
  returnLocation: string;
}

export function ToolCard(props: PropsWithChildren<ToolCardProps>) {
  const isBigScreen = useBigScreen();
  const navigation = useNavigate();
  return (
    <Form method="post">
      {!isBigScreen && (
        <StyledButtonGroup>
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
        </StyledButtonGroup>
      )}
      <Stack spacing={2} useFlexGap style={{ padding: "0.5rem " }}>
        {props.children}
      </Stack>
    </Form>
  );
}

const StyledButtonGroup = styled("div")(
  ({ theme }) => `
    display: flex;
    width: 100%;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    margin-bottom: 1rem;
    position: sticky;
    top: 3.5rem;
    background-color: ${theme.palette.background.paper};
    z-index: ${theme.zIndex.drawer + 1};
    border-radius: 0px;
    box-shadow: 0px 5px 5px rgba(0, 0, 0, 0.2);
    `
);
