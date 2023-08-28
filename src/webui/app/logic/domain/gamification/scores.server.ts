import { createCookie } from "@remix-run/node";
import { RecordScoreResult } from "jupiter-gen";
import { GLOBAL_PROPERTIES } from "~/global-properties-server";

// TODO(horia141): use createdtypedcookie
// TODO(horia141): secrets!
const scoreActionCookie = createCookie(
  GLOBAL_PROPERTIES.scoreActionCookieName,
  {
    maxAge: 60 * 60 * 24 * 30, // 30 days
  }
);

export async function saveScoreAction(result: RecordScoreResult) {
  return await scoreActionCookie.serialize({
    result: result,
  });
}
