import { Typography } from "@mui/material";
import type { PersonBirthday } from "jupiter-gen";
import { personBirthdayToStr } from "~/logic/domain/person-birthday";

interface BirthdayTagProps {
  birthday: PersonBirthday;
}

export function PersonBirthdayTag({ birthday }: BirthdayTagProps) {
  return (
    <Typography component={"span"}>
      Birthday is on {personBirthdayToStr(birthday)}
    </Typography>
  );
}
