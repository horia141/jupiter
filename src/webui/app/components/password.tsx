import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import { IconButton, InputAdornment, OutlinedInput } from "@mui/material";
import { useState } from "react";

interface PasswordProps {
  label: string;
  name: string;
  autoComplete?: "new-password" | "current-password";
  inputsEnabled: boolean;
}

export function Password(props: PasswordProps) {
  const [showPassword, setShowPassword] = useState(false);

  function handleClickShowPassword() {
    setShowPassword((show) => !show);
  }

  function handleMouseDownPassword(event: React.MouseEvent<HTMLButtonElement>) {
    event.preventDefault();
  }

  function handleMouseUpPassword(event: React.MouseEvent<HTMLButtonElement>) {
    event.preventDefault();
  }

  return (
    <OutlinedInput
      id={props.name}
      label={props.label}
      type={showPassword ? "text" : "password"}
      autoComplete={props.autoComplete}
      name={props.name}
      readOnly={!props.inputsEnabled}
      endAdornment={
        <InputAdornment position="end">
          <IconButton
            aria-label={
              showPassword ? "hide the password" : "display the password"
            }
            onClick={handleClickShowPassword}
            onMouseDown={handleMouseDownPassword}
            onMouseUp={handleMouseUpPassword}
            edge="end"
          >
            {showPassword ? <VisibilityOff /> : <Visibility />}
          </IconButton>
        </InputAdornment>
      }
      defaultValue={""}
    />
  );
}
