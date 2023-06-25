import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import DeleteIcon from "@mui/icons-material/Delete";
import {
  Card,
  CardActions,
  CardContent,
  IconButton,
  styled,
  useTheme,
} from "@mui/material";
import { Link } from "@remix-run/react";
import type { PanInfo } from "framer-motion";
import { motion, useMotionValue, useTransform } from "framer-motion";
import type { PropsWithChildren } from "react";
import { useBigScreen } from "~/rendering/use-big-screen";

const SWIPE_THRESHOLD = 200;
const SWIPE_COMPLETE_THRESHOLD = 150;

interface EntityCardProps {
  allowSwipe?: boolean;
  allowMarkDone?: boolean;
  allowMarkNotDone?: boolean;
  onMarkDone?: () => void;
  onMarkNotDone?: () => void;
}

export function EntityCard(props: PropsWithChildren<EntityCardProps>) {
  const isBigScreen = useBigScreen();

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
    info: PanInfo
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
    ]
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
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          touchAction: "pan-y",
          position: "relative",
          backgroundColor: "transparent",
        }}
      >
        <CardContent>{props.children}</CardContent>
        {isBigScreen && (
          <CardActions
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-end",
            }}
          >
            {props.allowMarkDone && (
              <IconButton
                size="medium"
                color="success"
                onClick={markDoneHandler}
              >
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
        )}
      </Card>
    </motion.div>
  );
}

interface EntityLinkProps {
  to: string;
}

export function EntityLink(props: PropsWithChildren<EntityLinkProps>) {
  return <StyledLink to={props.to}>{props.children}</StyledLink>;
}

const StyledLink = styled(Link)(({ theme }) => ({
  textDecoration: "none",
  color: theme.palette.info.dark,
  ":visited": {
    color: theme.palette.info.dark,
  },
  display: "flex",
  gap: "0.5rem",
  flexWrap: "wrap",
  alignItems: "center",
}));
