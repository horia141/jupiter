import { Typography } from "@mui/material";
import { useContext } from "react";
import { GlobalPropertiesContext } from "~/global-properties-client";

interface TitleProps {
  hideOnSmallScreen?: boolean;
}

export function Title(props: TitleProps) {
  const globalProperties = useContext(GlobalPropertiesContext);

  return (
    <Typography
      noWrap
      variant="h6"
      component="div"
      sx={{
        flexGrow: 1,
        display: {
          xs: props.hideOnSmallScreen ? "none" : "block",
          sm: "block",
        },
      }}
    >
      {globalProperties.title}
    </Typography>
  );
}
