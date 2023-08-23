import { redirect } from "@remix-run/node";
import { ShouldRevalidateFunction } from "@remix-run/react";
import { standardShouldRevalidate } from "~/rendering/standard-should-revalidate";
import { DisplayType } from "~/rendering/use-nested-entities";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader() {
  return redirect("/workspace/inbox-tasks");
}

export const shouldRevalidate: ShouldRevalidateFunction =
  standardShouldRevalidate;
