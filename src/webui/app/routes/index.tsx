import { redirect } from "@remix-run/node";
import { ShouldRevalidateFunction } from "@remix-run/react";

export const shouldRevalidate: ShouldRevalidateFunction = () => false;

export async function loader() {
  return redirect("/app");
}
