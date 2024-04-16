import { Eisen } from "@jupiter/webapi-client";

export function eisenIcon(eisen: Eisen): string {
  switch (eisen) {
    case Eisen.REGULAR:
      return "✳️";
    case Eisen.IMPORTANT:
      return "🛎️";
    case Eisen.URGENT:
      return "🔥";
    case Eisen.IMPORTANT_AND_URGENT:
      return "⚡";
  }
}

export function eisenName(eisen: Eisen): string {
  switch (eisen) {
    case Eisen.REGULAR:
      return "Regular";
    case Eisen.IMPORTANT:
      return "Important";
    case Eisen.URGENT:
      return "Urgent";
    case Eisen.IMPORTANT_AND_URGENT:
      return "Important And Urgent";
  }
}

const EISEN_MAP = {
  [Eisen.REGULAR]: 0,
  [Eisen.IMPORTANT]: 1,
  [Eisen.URGENT]: 2,
  [Eisen.IMPORTANT_AND_URGENT]: 3,
};

export function compareEisen(eisen1?: Eisen, eisen2?: Eisen): number {
  if (eisen1 === undefined && eisen2 === undefined) {
    return 0;
  } else if (eisen1 === undefined) {
    return -1;
  } else if (eisen2 === undefined) {
    return 1;
  } else {
    return EISEN_MAP[eisen1] - EISEN_MAP[eisen2];
  }
}
