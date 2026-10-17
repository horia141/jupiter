import { Apple as AppleIcon, Google as GoogleIcon } from "@mui/icons-material";
import { Alert, Button, Stack } from "@mui/material";
import { JupiterAuthProvider } from "@jupiter/webapi-client";
import { Link, useSubmit } from "react-router";
import { useContext, useState } from "react";

import { GlobalPropertiesContext } from "#/core/config-client";

const GOOGLE_PREPARE_LINK = "/app/lifecycle/init/google/prepare";
const APPLE_PREPARE_LINK = "/app/lifecycle/init/apple/prepare";
const GOOGLE_NATIVE_LINK = "/app/lifecycle/init/google/native";
const APPLE_NATIVE_LINK = "/app/lifecycle/init/apple/native";

export interface NativeSignInCode {
  code: string;
  // Only for Apple, which sends the name once and outside the token.
  userJson: string | null;
}

/**
 * Sign in through the SDKs of the app shell. Each returns an authorisation
 * code for the backend to exchange, or null when the user dismissed the sheet.
 */
export interface NativeSignInHandlers {
  signInWithGoogle: () => Promise<NativeSignInCode | null>;
  signInWithApple: (() => Promise<NativeSignInCode | null>) | null;
}

interface LifecycleOAuthProviderButtonsProps {
  disabled?: boolean;
  /**
   * Set when the app shell has the native sign in SDKs. The redirect flow
   * can't work there, because it leaves the app for the system browser.
   */
  nativeSignIn?: NativeSignInHandlers;
}

export function LifecycleOAuthProviderButtons({
  disabled = false,
  nativeSignIn,
}: LifecycleOAuthProviderButtonsProps) {
  const globalProperties = useContext(GlobalPropertiesContext);
  const submit = useSubmit();
  const [error, setError] = useState<string | null>(null);

  if (
    globalProperties.authProvider !== JupiterAuthProvider.LOCAL_GOOGLE_APPLE
  ) {
    return null;
  }

  async function handleNativeSignIn(provider: "google" | "apple") {
    if (nativeSignIn === undefined) {
      return;
    }

    setError(null);

    try {
      if (provider === "google") {
        const signedIn = await nativeSignIn.signInWithGoogle();
        if (signedIn !== null) {
          submit(
            { code: signedIn.code },
            { method: "post", action: GOOGLE_NATIVE_LINK },
          );
        }
      } else if (nativeSignIn.signInWithApple !== null) {
        const signedIn = await nativeSignIn.signInWithApple();
        if (signedIn !== null) {
          submit(
            signedIn.userJson === null
              ? { code: signedIn.code }
              : { code: signedIn.code, user: signedIn.userJson },
            { method: "post", action: APPLE_NATIVE_LINK },
          );
        }
      }
    } catch {
      setError("Could not sign in. Please try again.");
    }
  }

  return (
    <Stack spacing={1} sx={{ width: "100%" }}>
      {error !== null && <Alert severity="error">{error}</Alert>}
      <Stack spacing={1} direction="row" sx={{ width: "100%" }}>
        {nativeSignIn === undefined ? (
          <Button
            component={Link}
            to={GOOGLE_PREPARE_LINK}
            variant="outlined"
            fullWidth
            disabled={disabled}
            startIcon={<GoogleIcon />}
          >
            Google
          </Button>
        ) : (
          <Button
            variant="outlined"
            fullWidth
            disabled={disabled}
            startIcon={<GoogleIcon />}
            onClick={() => handleNativeSignIn("google")}
          >
            Google
          </Button>
        )}
        {nativeSignIn === undefined ? (
          <Button
            component={Link}
            to={APPLE_PREPARE_LINK}
            variant="outlined"
            fullWidth
            disabled={disabled}
            startIcon={<AppleIcon />}
          >
            Apple
          </Button>
        ) : (
          nativeSignIn.signInWithApple !== null && (
            <Button
              variant="outlined"
              fullWidth
              disabled={disabled}
              startIcon={<AppleIcon />}
              onClick={() => handleNativeSignIn("apple")}
            >
              Apple
            </Button>
          )
        )}
      </Stack>
    </Stack>
  );
}
