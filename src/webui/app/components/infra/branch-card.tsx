import { Container } from "@mui/material";
import { useLocation } from "@remix-run/react";
import { useIsPresent } from "framer-motion";
import { useEffect, useRef, type PropsWithChildren } from "react";
import { extractBranchFromPath } from "~/rendering/routes";
import { useScrollRestoration } from "~/rendering/scroll-restoration";
import { useBigScreen } from "~/rendering/use-big-screen";

export function BranchCard(props: PropsWithChildren) {
  const location = useLocation();
  const isPresent = useIsPresent();
  const isBigScreen = useBigScreen();

  const containerRef = useRef<HTMLDivElement>(null);

  useScrollRestoration(containerRef, extractBranchFromPath(location.pathname), isPresent);

  return (
    <Container
      ref={containerRef}
      maxWidth="lg"
      disableGutters
      style={{
        overflowY: "scroll",
        height: isBigScreen ? "calc(100vh - 4rem)" : "calc(100vh - 3.5rem)",
      }}
    >
      {props.children}
    </Container>
  );
}
