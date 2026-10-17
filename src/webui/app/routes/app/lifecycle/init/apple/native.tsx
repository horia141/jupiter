import { ApiError } from "@jupiter/webapi-client";
import type { ActionFunctionArgs } from "react-router";
import { redirectDocument } from "react-router";
import { StatusCodes } from "http-status-codes";
import { z } from "zod";
import { parseForm } from "zodix";
import { AUTH_TOKEN_NAME } from "@jupiter/core/infra/names";
import { getGuestApiClient } from "@jupiter/core/infra/api-clients.server";

import { emailVerificationVerifyUrl } from "~/routes/app/lifecycle/lifecycle-redirects.server";
import { commitSession, getSession } from "~/sessions";

const FormSchema = z.object({
  code: z.string(),
  user: z.string().optional(),
});

// The code comes from the Apple SDK in the app shell, so there is no redirect
// and no state cookie: the code is single use and only the backend, which holds
// the signing key, can exchange it.
// @secureFn
export async function action({ request }: ActionFunctionArgs) {
  const form = await parseForm(request, FormSchema);
  const session = await getSession(request.headers.get("Cookie"));
  const apiClient = await getGuestApiClient(request);

  try {
    const result = await apiClient.application.initCreateUserOrLoginAppleNative(
      {
        apple_auth_code: form.code,
        apple_user_json: form.user ?? null,
      },
    );

    session.set(AUTH_TOKEN_NAME, result.auth_token_ext);

    return redirectDocument(
      emailVerificationVerifyUrl(result.new_user.ref_id),
      {
        headers: { "Set-Cookie": await commitSession(session) },
      },
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === StatusCodes.CONFLICT) {
      return redirectDocument("/app/lifecycle/util/user-already-exists");
    }

    throw error;
  }
}
