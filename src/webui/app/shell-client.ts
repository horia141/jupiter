import { AppShell } from "@jupiter/webapi-client";

export function shouldShowLargeAppBar(appShell: AppShell): boolean {
  return (
    appShell === AppShell.MOBILE_CAPACITOR || appShell === AppShell.MOBILE_PWA
  );
}
