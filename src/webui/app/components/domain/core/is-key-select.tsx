import { ToggleButton } from "@mui/material";
import KeyIcon from "@mui/icons-material/Key";
import { useEffect, useState } from "react";

interface IsKeySelectProps {
  name: string;
  value?: boolean;
  defaultValue?: boolean;
  onChange?: (value: boolean) => void;
}

export function IsKeySelect(props: IsKeySelectProps) {
  const [value, setValue] = useState(
    props.value ?? props.defaultValue ?? false,
  );
  useEffect(() => {
    setValue(props.value ?? props.defaultValue ?? false);
  }, [props.value, props.defaultValue]);

  return (
    <>
      <ToggleButton
        value={props.name}
        selected={value}
        onChange={() => setValue((prevSelected) => !prevSelected)}
        sx={{ height: "100%" }}
      >
        <KeyIcon />
      </ToggleButton>
      {value && <input type="hidden" name={props.name} value={"on"} />}
    </>
  );
}
