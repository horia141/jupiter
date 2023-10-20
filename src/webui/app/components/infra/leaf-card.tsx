import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import DeleteIcon from "@mui/icons-material/Delete";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";
import { Box, ButtonGroup, IconButton, styled } from "@mui/material";
import { Form, Link, useLocation, useNavigate } from "@remix-run/react";
import { useIsPresent } from "framer-motion";
import { useEffect, useRef, type PropsWithChildren } from "react";
import { useScrollRestoration } from "~/rendering/scroll-restoration";
import { useBigScreen } from "~/rendering/use-big-screen";

interface LeafCardProps {
  showArchiveButton?: boolean;
  enableArchiveButton?: boolean;
  returnLocation: string;
}

export function LeafCard(props: PropsWithChildren<LeafCardProps>) {
  const isBigScreen = useBigScreen();
  const navigation = useNavigate();
  const location = useLocation();
  const isPresent = useIsPresent();

  const containerRef = useRef<HTMLDivElement>(null);

  useScrollRestoration(containerRef, location.pathname, isPresent);

  return (
    <Form method="post">
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
      <Box
        ref={containerRef}
        style={{
          padding: "0.5rem ",
          height: `calc(100vh - 4rem - ${isBigScreen ? "4rem" : "3.5rem"})`,
          overflowY: "scroll",
        }}
      >
        {props.children}
      </Box>
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
    height: 3rem;
    background-color: ${theme.palette.background.paper};
    z-index: ${theme.zIndex.drawer + 1};
    border-radius: 0px;
    box-shadow: 0px 5px 5px rgba(0, 0, 0, 0.2);
    `
);
