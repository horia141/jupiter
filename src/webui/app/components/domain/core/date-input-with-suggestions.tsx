
import { ADate } from "@jupiter/webapi-client";
import { useEffect, useState } from "react";
import {
  Button,
  ButtonGroup,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  OutlinedInput,
  Stack,
} from "@mui/material";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";

import { strToADate } from "~/logic/domain/adate";
import { SuggestedDate } from "~/logic/domain/suggested-date";

interface DateInputWithSuggestionsProps {
  name: string;
  label: string;
  inputsEnabled: boolean;
  value?: ADate | null;
  onChange?: (date: ADate) => void;
  defaultValue?: ADate | null;
  suggestedDates?: SuggestedDate[];
}

export function DateInputWithSuggestions(props: DateInputWithSuggestionsProps) {
  const [date, setDate] = useState<ADate | undefined>(
    props.value || props.defaultValue || undefined,
  );
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  useEffect(() => {
    setDate(props.value || props.defaultValue || undefined);
  }, [props.value, props.defaultValue]);

  const handleSuggestedDateClick = (suggestedDate: SuggestedDate) => {
    setDate(suggestedDate.date);
    props.onChange?.(suggestedDate.date);
    setIsDialogOpen(false);
  };

  return (
    <Stack direction="row" spacing={1} alignItems="center">
      <OutlinedInput
        type="date"
        label={props.label}
        readOnly={!props.inputsEnabled}
        name={props.name}
        notched
        value={date}
        onChange={(e) => {
          const newDate = strToADate(e.target.value as ADate);
          setDate(newDate);
          props.onChange?.(newDate);
        }}
        sx={{ flexGrow: 1 }}
      />
      {props.suggestedDates && props.suggestedDates.length > 0 && (
        <>
          <IconButton
            onClick={() => setIsDialogOpen(true)}
            disabled={!props.inputsEnabled}
            size="small"
          >
            <CalendarMonthIcon />
          </IconButton>
          <Dialog
            open={isDialogOpen}
            onClose={() => setIsDialogOpen(false)}
            maxWidth="xs"
            fullWidth
            disablePortal
          >
            <DialogTitle>Suggested Dates</DialogTitle>
            <DialogContent>
              <ButtonGroup orientation="vertical" fullWidth sx={{ mt: 1 }}>
                {props.suggestedDates.map((suggestedDate) => (
                  <Button
                    key={suggestedDate.label}
                    onClick={() => handleSuggestedDateClick(suggestedDate)}
                    variant={
                      date === suggestedDate.date ? "contained" : "outlined"
                    }
                  >
                    {suggestedDate.label}
                  </Button>
                ))}
              </ButtonGroup>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setIsDialogOpen(false)}>Close</Button>
            </DialogActions>
          </Dialog>
        </>
      )}
    </Stack>
  );
}
