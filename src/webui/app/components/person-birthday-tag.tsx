import { Typography } from "@mui/material";
import type { PersonBirthday } from "@jupiter/webapi-client";

interface BirthdayTagProps {
  birthday: PersonBirthday;
}

export function PersonBirthdayTag({ birthday }: BirthdayTagProps) {
  return <Typography component={"span"}>Birthday is on {birthday}</Typography>;
}
