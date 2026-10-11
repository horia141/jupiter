declare global {
  interface Window {
    /** The origin of the app shell's local pages, injected by Capacitor. */
    WEBVIEW_SERVER_URL?: string;
  }
}

export {};
