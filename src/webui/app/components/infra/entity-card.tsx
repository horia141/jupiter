import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import DeleteIcon from "@mui/icons-material/Delete";
import {
  Card,
  CardActions,
  CardContent,
  IconButton,
  useTheme,
} from "@mui/material";
import type { PanInfo } from "framer-motion";
import { motion, useMotionValue, useTransform } from "framer-motion";
import type { PropsWithChildren } from "react";

import { useBigScreen } from "~/rendering/use-big-screen";
import { FakeLink, StandardLink } from "~/components/infra/standard-link";

const SWIPE_THRESHOLD = 200;
const SWIPE_COMPLETE_THRESHOLD = 150;

interface EntityCardProps {
  entityId?: string;
  showAsArchived?: boolean;
  backgroundHint?: "neutral" | "success" | "failure" | "warning";
  extraControls?: JSX.Element;
  allowSwipe?: boolean;
  allowSelect?: boolean;
  selected?: boolean;
  allowMarkDone?: boolean;
  allowMarkNotDone?: boolean;
  indent?: number;
  markButtonsStyle?: "row" | "column";
  onClick?: () => void;
  onMarkDone?: () => void;
  onMarkNotDone?: () => void;
}

export function EntityCard(props: PropsWithChildren<EntityCardProps>) {
  const isBigScreen = useBigScreen();
  const backgroundHint = props.backgroundHint || "neutral";

  const theme = useTheme();

  function markDoneHandler() {
    if (props.allowMarkDone && props.onMarkDone) {
      props.onMarkDone();
    }
  }

  function markNotDoneHandler() {
    if (props.allowMarkNotDone && props.onMarkNotDone) {
      props.onMarkNotDone();
    }
  }

  function onDragEnd(
    event: MouseEvent | TouchEvent | PointerEvent,
    info: PanInfo,
  ) {
    if (info.offset.x < -SWIPE_COMPLETE_THRESHOLD) {
      if (props.allowMarkDone && props.onMarkDone) {
        props.onMarkDone();
      }
    } else if (info.offset.x < SWIPE_COMPLETE_THRESHOLD) {
      // do nothing
    } else {
      if (props.allowMarkNotDone && props.onMarkNotDone) {
        props.onMarkNotDone();
      }
    }
  }

  const x = useMotionValue(0);
  const background = useTransform(
    x,
    [-SWIPE_COMPLETE_THRESHOLD, 0, SWIPE_COMPLETE_THRESHOLD],
    [
      theme.palette.success.light,
      theme.palette.background.paper,
      theme.palette.warning.light,
    ],
  );

  return (
    <motion.div
      drag={props.allowSwipe ? "x" : false}
      whileDrag={{ scale: 1.1 }}
      dragSnapToOrigin={true}
      dragElastic={0.1}
      dragConstraints={{
        left: props.allowMarkDone ? -SWIPE_THRESHOLD : 0,
        right: props.allowMarkNotDone ? SWIPE_THRESHOLD : 0,
      }}
      onDragEnd={onDragEnd}
      style={{ x, background }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, height: "0px", marginTop: "0px" }}
      transition={{ duration: 1 }}
    >
      <Card
        id={props.entityId}
        sx={{
          display: "flex",
          marginLeft: props.indent ? `${props.indent}rem` : "0",
          justifyContent: "space-between",
          alignItems: "center",
          touchAction: "pan-y",
          position: "relative",
          boxShadow:
            props.allowSelect && props.selected
              ? `inset 0 0 4px ${theme.palette.primary.main};`
              : undefined,
          backgroundColor:
            backgroundHint === "neutral"
              ? props.showAsArchived
                ? theme.palette.action.hover
                : "transparent"
              : backgroundHint === "success"
                ? `${theme.palette.success.light}22`
                : backgroundHint === "warning"
                  ? `${theme.palette.warning.light}22`
                  : `${theme.palette.error.light}22`,
        }}
        onClick={props.onClick}
      >
        <CardContent sx={{ flexGrow: "1", padding: "0px" }}>
          {props.children}
        </CardContent>

        <CardActions
          sx={{
            display: "flex",
            flexDirection: props.markButtonsStyle || "row",
            alignItems: "flex-end",
          }}
        >
          {props.extraControls}
          {isBigScreen && props.allowMarkDone && (
            <IconButton size="medium" color="success" onClick={markDoneHandler}>
              <CheckCircleIcon fontSize="medium" />
            </IconButton>
          )}
          {props.allowMarkNotDone && (
            <IconButton
              size="medium"
              color="warning"
              onClick={markNotDoneHandler}
            >
              <DeleteIcon fontSize="medium" />
            </IconButton>
          )}
        </CardActions>
      </Card>
    </motion.div>
  );
}

interface EntityLinkProps {
  to: string;
  block?: boolean;
  light?: boolean;
  inline?: boolean;
}

export function EntityLink(props: PropsWithChildren<EntityLinkProps>) {
  if (!(props.block === true)) {
    return (
      <StandardLink
        onMouseDown={(e) => e.preventDefault()}
        to={props.to}
        inline={props.inline === true ? "true" : "false"}
        light={props.light === true ? "true" : "false"}
      >
        {props.children}
      </StandardLink>
    );
  } else {
    return (
      <EntityFakeLink inline={props.inline} light={props.light}>
        {props.children}
      </EntityFakeLink>
    );
  }
}

interface EntityFakeLinkProps {
  inline?: boolean;
  light?: boolean;
}

export function EntityFakeLink(props: PropsWithChildren<EntityFakeLinkProps>) {
  return (
    <FakeLink
      inline={props.inline ? "true" : "false"}
      light={props.light ? "true" : "false"}
    >
      {props.children}
    </FakeLink>
  );
}
