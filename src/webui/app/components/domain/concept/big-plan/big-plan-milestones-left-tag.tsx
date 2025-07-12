import { SlimChip } from "~/components/infra/chips";

interface Props {
  milestonesLeft: number;
}

export function BigPlanMilestonesLeftTag(props: Props) {
  const milestonePlural = props.milestonesLeft === 1 ? "milestone" : "milestones";
  return <SlimChip label={`${props.milestonesLeft} ${milestonePlural} left`} color="info" />;
}
