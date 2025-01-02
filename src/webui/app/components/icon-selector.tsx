import { Button, ButtonGroup, OutlinedInput } from "@mui/material";
import type { EmojiClickData } from "emoji-picker-react";
import EmojiPicker, { EmojiStyle } from "emoji-picker-react";
import { useState } from "react";
import { ClientOnly } from "remix-utils";

interface Props {
  defaultIcon?: string | null;
  readOnly: boolean;
}

export function IconSelector({ defaultIcon, readOnly }: Props) {
  const [selectedIcon, setSelectedIcon] = useState(defaultIcon);
  const [showIconSelector, setShowIconSelector] = useState(false);

  function handleClear() {
    setSelectedIcon("");
  }

  function handleChoose() {
    setShowIconSelector((i) => !i);
  }

  function handleSelect(emojiData: EmojiClickData, event: MouseEvent) {
    setSelectedIcon(emojiData.emoji);
    setShowIconSelector(false);
  }

  return (
    <>
      <OutlinedInput
        label="Icon"
        name="icon"
        readOnly={true}
        value={selectedIcon}
        endAdornment={
          <ButtonGroup>
            <Button onClick={handleClear}>Clear</Button>
            <Button
              disabled={readOnly}
              variant={showIconSelector ? "contained" : "outlined"}
              onClick={handleChoose}
            >
              Choose
            </Button>
          </ButtonGroup>
        }
      />

      {showIconSelector && (
        <ClientOnly fallback={<span>{defaultIcon}</span>}>
          {() => (
            <EmojiPicker
              width="auto"
              autoFocusSearch={false}
              allowExpandReactions={false}
              emojiStyle={EmojiStyle.NATIVE}
              onEmojiClick={handleSelect}
            />
          )}
        </ClientOnly>
      )}
    </>
  );
}
