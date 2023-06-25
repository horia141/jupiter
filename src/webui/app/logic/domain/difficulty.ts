import { Difficulty } from "jupiter-gen";

export function difficultyName(difficulty: Difficulty): string {
  switch (difficulty) {
    case Difficulty.EASY:
      return "Easy";
    case Difficulty.MEDIUM:
      return "Medium";
    case Difficulty.HARD:
      return "Hard";
  }
}

const DIFFICULTY_MAP = {
  [Difficulty.EASY]: 0,
  [Difficulty.MEDIUM]: 1,
  [Difficulty.HARD]: 2,
};

export function compareDifficulty(
  difficulty1?: Difficulty,
  difficulty2?: Difficulty
): number {
  if (difficulty1 === undefined && difficulty2 === undefined) {
    return 0;
  } else if (difficulty1 === undefined) {
    return -1;
  } else if (difficulty2 === undefined) {
    return 1;
  } else {
    return DIFFICULTY_MAP[difficulty1] - DIFFICULTY_MAP[difficulty2];
  }
}
