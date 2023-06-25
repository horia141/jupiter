import type { ChipProps } from "@mui/material";
import { Chip, styled } from "@mui/material";

export const SlimChip = styled(Chip)<ChipProps>(({ theme }) => ({
  maxWidth: "130px",
  fontSize: "0.75rem",
  lineHeight: "1rem",
  height: "1rem",
}));
