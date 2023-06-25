import { useMediaQuery, useTheme } from "@mui/material";

export function useBigScreen(): boolean {
  const theme = useTheme();
  return useMediaQuery(theme.breakpoints.up("md"));
}
