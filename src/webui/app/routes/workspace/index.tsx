import { redirect } from "@remix-run/node";
import { DisplayType } from "~/rendering/use-nested-entities";

export const handle = {
  displayType: DisplayType.TRUNK,
};

export async function loader() {
  return redirect("/workspace/inbox-tasks");
}
