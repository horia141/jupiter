import { Typography } from "@mui/material";
import { useContext } from "react";
import { GlobalPropertiesContext } from "~/global-properties-client";

export function Title() {
  const globalProperties = useContext(GlobalPropertiesContext);

  return (
    <Typography
      noWrap
      variant="h6"
      component="div"
      sx={{ flexGrow: 1, display: { xs: "none", sm: "block" } }}
    >
      {globalProperties.title}
    </Typography>
  );
}
