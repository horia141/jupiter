import { SlimChip } from "~/components/infra/chips";

interface Props {
  donePct: number;
}

export function BigPlanDonePctTag(props: Props) {
  const tagClass = donePctToClass(props.donePct);
  return <SlimChip label={`[${props.donePct}%]`} color={tagClass} />;
}

function donePctToClass(donePct: number) {
  if (donePct === 0) {
    return "error";
  } else if (donePct === 100) {
    return "success";
  } else {
    return "info";
  }
}
