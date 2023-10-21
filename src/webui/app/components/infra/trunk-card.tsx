import { Container } from "@mui/material";
import { useLocation } from "@remix-run/react";
import { useIsPresent } from "framer-motion";
import { useEffect, useRef, type PropsWithChildren } from "react";
import { extractTrunkFromPath } from "~/rendering/routes";
import {
  restoreScrollPosition,
  saveScrollPosition,
} from "~/rendering/scroll-restoration";
import { useBigScreen } from "~/rendering/use-big-screen";

export function TrunkCard(props: PropsWithChildren) {
  const location = useLocation();
  const isBigScreen = useBigScreen();

  const containerRef = useRef<HTMLDivElement>(null);

  const isPresent = useIsPresent();

  function handleScroll(ref: HTMLDivElement, pathname: string) {
    if (!isPresent) {
      return;
    }
    saveScrollPosition(ref, pathname);
  }

  useEffect(() => {
    if (containerRef.current === null) {
      return;
    }

    if (!isPresent) {
      return;
    }

    function handleScrollSpecial() {
      handleScroll(
        containerRef.current!,
        extractTrunkFromPath(location.pathname)
      );
    }

    restoreScrollPosition(
      containerRef.current,
      extractTrunkFromPath(location.pathname)
    );
    containerRef.current.addEventListener("scrollend", handleScrollSpecial);

    return () => {
      containerRef.current?.removeEventListener(
        "scrollend",
        handleScrollSpecial
      );
    };
  }, [containerRef, location]);

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
