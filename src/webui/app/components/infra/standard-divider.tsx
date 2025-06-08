import { Divider, Typography } from "@mui/material";

interface StandardDividerProps {
  title: string;
  size: "small" | "medium" | "large";
}

export function StandardDivider(props: StandardDividerProps) {
  return (
    <Divider variant="fullWidth">
      <Typography
        variant={
          props.size === "small"
            ? "subtitle2"
            : props.size === "medium"
              ? "subtitle2"
              : "h6"
        }
        sx={{
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {props.title}
      </Typography>
    </Divider>
  );
}
