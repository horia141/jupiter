import { redirect } from "@remix-run/node";
import type { ShouldRevalidateFunction } from "@remix-run/react";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader() {
  return redirect("/app/workspace/inbox-tasks");
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;
