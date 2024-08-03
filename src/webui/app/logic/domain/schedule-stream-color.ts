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
