import type { ActionFunctionArgs } from "@remix-run/node";
import { redirect } from "@remix-run/node";

import { destroySession, getSession } from "~/sessions";

// @secureFn
export async function loader() {
  return redirect("/");
}

// @secureFn
export async function action({ request }: ActionFunctionArgs) {
  const session = await getSession(request.headers.get("Cookie"));
  return redirect("/app/login", {
    headers: {
      "Set-Cookie": await destroySession(session),
    },
  });
}
