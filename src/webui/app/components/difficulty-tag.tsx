import { Difficulty } from "jupiter-gen";
import { difficultyName } from "~/logic/domain/difficulty";
import { SlimChip } from "./infra/chips";

interface Props {
  difficulty: Difficulty;
}

export function DifficultyTag(props: Props) {
  const tagName = difficultyName(props.difficulty);
  const tagClass = difficultyToClass(props.difficulty);
  return <SlimChip label={tagName} color={tagClass} />;
}

function difficultyToClass(difficulty: Difficulty) {
  switch (difficulty) {
    case Difficulty.EASY:
      return "default";
    case Difficulty.MEDIUM:
      return "warning";
    case Difficulty.HARD:
      return "error";
  }
}
