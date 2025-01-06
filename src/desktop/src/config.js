export async function getWebUiUrl() {
  const asUrl = new URL(window.WEBUI_URL);

  asUrl.searchParams.set("clientVersion", window.CLIENT_VERSION);
  asUrl.searchParams.set("initialWindowWidth", window.INITIAL_WINDOW_WIDTH);

  return asUrl;
}
