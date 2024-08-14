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

export function scheduleStreamColorHex(color: ScheduleStreamColor): string {
  switch (color) {
    case ScheduleStreamColor.BLUE:
      return "#2196f3";
    case ScheduleStreamColor.GREEN:
      return "#4caf50";
    case ScheduleStreamColor.RED:
      return "#f44336";
    case ScheduleStreamColor.YELLOW:
      return "#ffeb3b";
    case ScheduleStreamColor.PURPLE:
      return "#9c27b0";
    case ScheduleStreamColor.ORANGE:
      return "#ff9800";
    case ScheduleStreamColor.GRAY:
      return "#9e9e9e";
    case ScheduleStreamColor.BROWN:
      return "#795548";
    case ScheduleStreamColor.CYAN:
      return "#00bcd4";
    case ScheduleStreamColor.MAGENTA:
      return "#e91e63";
  }
}
