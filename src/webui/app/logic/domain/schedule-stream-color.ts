import { ScheduleStreamColor } from "@jupiter/webapi-client";

export function scheduleStreamColorName(color: ScheduleStreamColor): string {
  switch (color) {
    case ScheduleStreamColor.BLUE:
      return "Blue";
    case ScheduleStreamColor.GREEN:
      return "Green";
    case ScheduleStreamColor.RED:
      return "Red";
    case ScheduleStreamColor.YELLOW:
      return "Yellow";
    case ScheduleStreamColor.PURPLE:
      return "Purple";
    case ScheduleStreamColor.ORANGE:
      return "Orange";
    case ScheduleStreamColor.GRAY:
      return "Gray";
    case ScheduleStreamColor.BROWN:
      return "Brown";
    case ScheduleStreamColor.CYAN:
      return "Cyan";
    case ScheduleStreamColor.MAGENTA:
      return "Magenta";
  }
}

export function scheduleStreamColorHex(
  color: ScheduleStreamColor,
  modify?: "lighter" | "darker" | "normal"
): string {
  let hexColor: string;
  switch (color) {
    case ScheduleStreamColor.BLUE:
      hexColor = "#2196f3";
      break;
    case ScheduleStreamColor.GREEN:
      hexColor = "#4caf50";
      break;
    case ScheduleStreamColor.RED:
      hexColor = "#f44336";
      break;
    case ScheduleStreamColor.YELLOW:
      hexColor = "#f7d560";
      break;
    case ScheduleStreamColor.PURPLE:
      hexColor = "#9c27b0";
      break;
    case ScheduleStreamColor.ORANGE:
      hexColor = "#ff9800";
      break;
    case ScheduleStreamColor.GRAY:
      hexColor = "#9e9e9e";
      break;
    case ScheduleStreamColor.BROWN:
      hexColor = "#795548";
      break;
    case ScheduleStreamColor.CYAN:
      hexColor = "#00bcd4";
      break;
    case ScheduleStreamColor.MAGENTA:
      hexColor = "#e91e63";
      break;
  }

  if (modify === "lighter") {
    return adjustColor(hexColor, 30);
  } else if (modify === "darker") {
    return adjustColor(hexColor, -30);
  } else {
    return hexColor;
  }
}

export function scheduleStreamColorContrastingHex(
  color: ScheduleStreamColor
): string {
  switch (color) {
    case ScheduleStreamColor.BLUE:
      return "#ffffff";
    case ScheduleStreamColor.GREEN:
      return "#ffffff";
    case ScheduleStreamColor.RED:
      return "#ffffff";
    case ScheduleStreamColor.YELLOW:
      return "#000000";
    case ScheduleStreamColor.PURPLE:
      return "#ffffff";
    case ScheduleStreamColor.ORANGE:
      return "#000000";
    case ScheduleStreamColor.GRAY:
      return "#000000";
    case ScheduleStreamColor.BROWN:
      return "#ffffff";
    case ScheduleStreamColor.CYAN:
      return "#000000";
    case ScheduleStreamColor.MAGENTA:
      return "#ffffff";
  }
}

function adjustColor(hex: string, amount: number): string {
  let usePound = false;

  if (hex[0] === "#") {
    hex = hex.slice(1);
    usePound = true;
  }

  let num = parseInt(hex, 16);

  let r = (num >> 16) + amount;
  if (r > 255) r = 255;
  else if (r < 0) r = 0;

  let g = ((num >> 8) & 0x00ff) + amount;
  if (g > 255) g = 255;
  else if (g < 0) g = 0;

  let b = (num & 0x0000ff) + amount;
  if (b > 255) b = 255;
  else if (b < 0) b = 0;

  return (
    (usePound ? "#" : "") +
    ((r << 16) | (g << 8) | b).toString(16).padStart(6, "0")
  );
}
