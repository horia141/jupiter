import { useContext, useMemo } from "react";
import { AppPlatform, AppShell } from "@jupiter/webapi-client";
import { hasShellFeature, ShellFeature } from "@jupiter/core/frontdoor";
import type {
  NativeSignInCode,
  NativeSignInHandlers,
} from "@jupiter/core/auth/component/lifecycle-oauth-provider-buttons";

import { ServicePropertiesContext } from "~/logic/config";
import type { NativeSignInConfig } from "~/logic/config";

/**
 * Sign in through the Google and Apple SDKs of the mobile app shell. Neither
 * returns a session: they hand back an authorisation code, which the backend
 * exchanges the same way it does for the redirect flow, but with no redirect.
 */

/**
 * What the OAuth buttons need in this shell. In the mobile app the redirect flow
 * can't work, so without native sign in (an older build) the buttons are off.
 */
export function useOAuthProviderButtonProps(): {
  disabled: boolean;
  nativeSignIn?: NativeSignInHandlers;
} {
  const serviceProperties = useContext(ServicePropertiesContext);
  const { frontDoorInfo, nativeSignIn: config } = serviceProperties;

  const hasNativeSignIn = hasShellFeature(
    frontDoorInfo,
    ShellFeature.NATIVE_SIGN_IN,
  );
  const handlers = useMemo(
    () =>
      hasNativeSignIn
        ? nativeSignInHandlers(config, frontDoorInfo.appPlatform)
        : undefined,
    [hasNativeSignIn, config, frontDoorInfo.appPlatform],
  );

  return {
    disabled:
      frontDoorInfo.appShell === AppShell.MOBILE_CAPACITOR && !hasNativeSignIn,
    nativeSignIn: handlers,
  };
}

function nativeSignInHandlers(
  config: NativeSignInConfig,
  appPlatform: AppPlatform,
): NativeSignInHandlers {
  return {
    signInWithGoogle: () => signInWithGoogleNatively(config),
    // Android has no native Sign in with Apple, only the redirect flow. The
    // platform comes from the frontdoor, not Capacitor, so the server render
    // and the client agree.
    signInWithApple:
      appPlatform === AppPlatform.MOBILE_IOS ||
      appPlatform === AppPlatform.TABLET_IOS
        ? signInWithAppleNatively
        : null,
  };
}

export async function signInWithGoogleNatively(
  config: NativeSignInConfig,
): Promise<NativeSignInCode | null> {
  const { SocialLogin } = await import("@capgo/capacitor-social-login");

  await SocialLogin.initialize({
    google: {
      webClientId: config.googleWebClientId,
      iOSClientId: config.googleIosClientId,
      // Required for offline mode on iOS, and the same as the web client.
      iOSServerClientId: config.googleWebClientId,
      // Offline mode returns a serverAuthCode instead of tokens.
      mode: "offline",
    },
  });

  try {
    const { result } = await SocialLogin.login({
      provider: "google",
      options: {},
    });

    if (!("serverAuthCode" in result)) {
      throw new Error("Google sign in did not return an authorisation code");
    }

    return { code: result.serverAuthCode, userJson: null };
  } catch (error) {
    if (isCancellation(error)) {
      return null;
    }
    throw error;
  }
}

export async function signInWithAppleNatively(): Promise<NativeSignInCode | null> {
  const { SocialLogin } = await import("@capgo/capacitor-social-login");

  await SocialLogin.initialize({
    apple: {
      // An empty redirect stops the plugin from calling a backend itself.
      redirectUrl: "",
      // Return the raw authorisation code, for the backend to exchange.
      useProperTokenExchange: true,
    },
  });

  try {
    const { result } = await SocialLogin.login({
      provider: "apple",
      options: { scopes: ["name", "email"] },
    });

    if (!result.authorizationCode) {
      throw new Error("Apple sign in did not return an authorisation code");
    }

    // The shape Apple's own redirect flow sends in its `user` field.
    const userJson =
      result.profile.givenName || result.profile.familyName
        ? JSON.stringify({
            name: {
              firstName: result.profile.givenName ?? "",
              lastName: result.profile.familyName ?? "",
            },
          })
        : null;

    return { code: result.authorizationCode, userJson };
  } catch (error) {
    if (isCancellation(error)) {
      return null;
    }
    throw error;
  }
}

function isCancellation(error: unknown): boolean {
  const message = error instanceof Error ? error.message : String(error);
  return /cancel|dismiss|1001|12501/i.test(message);
}
