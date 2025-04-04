import CloseIcon from "@mui/icons-material/Close";
import MoreHorizIcon from "@mui/icons-material/MoreHoriz";
import { Button, ButtonGroup, IconButton, styled } from "@mui/material";
import { AnimatePresence, motion } from "framer-motion";
import { Fragment, useState } from "react";

interface ExtraControlsProps {
  isBigScreen: boolean;
  controls: JSX.Element[];
}

export function ExtraControls({ isBigScreen, controls }: ExtraControlsProps) {
  const [showFullControls, setShowFullControls] = useState(false);

  if (isBigScreen) {
    return (
      <ExtraControlsBigScreenContainer>
        {controls.map((c, i) => (
          <Fragment key={i}>{c}</Fragment>
        ))}
      </ExtraControlsBigScreenContainer>
    );
  } else if (controls.length === 0) {
    return null;
  } else if (controls.length === 1) {
    return (
      <ExtraControlsBigScreenContainer>
        {controls[0]}
      </ExtraControlsBigScreenContainer>
    );
  }

  return (
    <>
      {!showFullControls && (
        <Button
          variant="outlined"
          sx={{ margin: "0.5rem" }}
          onClick={() => setShowFullControls(true)}
        >
          <MoreHorizIcon />
        </Button>
      )}

      <AnimatePresence>
        {showFullControls && (
          <ExtraControlsFrame
            key="trunk-panel-extra-controls"
            initial={{ opacity: 1, x: "100vw" }}
            animate={{ opacity: 1, x: "0vw" }}
            exit={{ opacity: 1, x: "100vw" }}
            transition={{ duration: 0.4 }}
          >
            <ExtraControlsSmallScreenContainer>
              <div style={{ width: "max-content" }}>
                {controls.map((c, i) => (
                  <Fragment key={i}>{c}</Fragment>
                ))}
              </div>
            </ExtraControlsSmallScreenContainer>
            <IconButton
              onClick={() => setShowFullControls(false)}
              sx={{ marginLeft: "auto" }}
            >
              <CloseIcon />
            </IconButton>
          </ExtraControlsFrame>
        )}
      </AnimatePresence>
    </>
  );
}

const ExtraControlsFrame = styled(motion.div)(() => ({
  position: "absolute",
  left: "0px",
  top: "0px",
  height: "3rem",
  backgroundColor: "white",
  display: "flex",
  paddingLeft: "0.5rem",
  paddingRight: "0.5rem",
  alignItems: "center",
  width: "100%",
  justifyContent: "space-between",
}));

const ExtraControlsBigScreenContainer = styled(ButtonGroup)(() => ({
  paddingTop: "0.5rem",
  paddingBottom: "0.5rem",
  paddingRight: "0.5rem",
}));

const ExtraControlsSmallScreenContainer = styled(ButtonGroup)(() => ({
  overflowX: "scroll",
  display: "block",
  paddingTop: "0.5rem",
  paddingBottom: "0.5rem",
  paddingRight: "0.5rem",
  width: "calc(80vw)",
}));
