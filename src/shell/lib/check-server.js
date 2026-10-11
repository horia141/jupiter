/**
 * Checks that a user-provided address points at a compatible Thrive server.
 *
 * Shared by the desktop and mobile shells. It never talks to the network
 * itself: each platform passes an `httpGet(url)` that does a GET without
 * following redirects (to dodge CORS and see the redirect as it is) and
 * resolves to `{ status, headers }`.
 */

export const VERSION_HEADER = "X-Jupiter-Version";

const SCHEME_RE = /^[a-z][a-z0-9+.-]*:\/\//i;
// Hosts that only make sense for a server running on the developer's machine
// (or, for 10.0.2.2, on the machine hosting an Android emulator).
const LOCAL_HOST_RE =
  /^(localhost|127\.\d+\.\d+\.\d+|10\.0\.2\.2|\[::1\])(:\d+)?(\/|$)/i;

/**
 * @param {string} input What the user typed.
 * @param {object} options
 * @param {(url: string) => Promise<{status: number, headers: Record<string, string>}>} options.httpGet
 * @param {boolean} options.allowHttp Whether plain http:// servers are allowed (local builds only).
 * @param {string} options.clientVersion This app's version, e.g. "1.3.3".
 * @returns {Promise<{result: "ok", serverUrl: string} | {result: "error", errorMsg: string}>}
 */
export async function checkServer(
  input,
  { httpGet, allowHttp, clientVersion },
) {
  let serverUrl;
  try {
    serverUrl = normalizeServerUrl(input, { allowHttp });
  } catch (error) {
    return { result: "error", errorMsg: error.message };
  }

  let response;
  try {
    response = await fetchLatestVersions(httpGet, serverUrl);
    const location = getHeader(response, "Location");
    if (
      getHeader(response, VERSION_HEADER) === null &&
      location !== null &&
      location.startsWith("https://")
    ) {
      // A self-hosted server redirects http to https first, so the answer we
      // want is one redirect further along.
      response = await fetchLatestVersions(httpGet, new URL(location));
    }
  } catch (error) {
    return {
      result: "error",
      errorMsg: `Could not reach the server: ${describeError(error)}`,
    };
  }

  const remoteVersion = getHeader(response, VERSION_HEADER);
  if (remoteVersion === null) {
    return {
      result: "error",
      errorMsg: "The server doesn't appear to be a Thrive server",
    };
  }

  const remoteMajor = parseMajor(remoteVersion);
  if (remoteMajor === null) {
    return {
      result: "error",
      errorMsg: `The server reports an unexpected version: ${remoteVersion}`,
    };
  }

  if (parseMajor(clientVersion) !== remoteMajor) {
    return {
      result: "error",
      errorMsg: `This app's version ${clientVersion} is incompatible with the server's ${remoteVersion}`,
    };
  }

  return { result: "ok", serverUrl: serverUrl.toString() };
}

/**
 * Turns what the user typed into the server's root URL, or throws an Error
 * whose message can be shown to them.
 */
export function normalizeServerUrl(input, { allowHttp }) {
  let clean = input.trim().replace(/^['"]|['"]$/g, "");
  if (clean === "") {
    throw new Error("Please enter a server address");
  }

  if (!SCHEME_RE.test(clean)) {
    const scheme = allowHttp && LOCAL_HOST_RE.test(clean) ? "http" : "https";
    clean = `${scheme}://${clean}`;
  }

  let url;
  try {
    url = new URL(clean);
  } catch {
    throw new Error("That doesn't look like a valid address");
  }

  if (url.protocol === "http:" && !allowHttp) {
    throw new Error("Only https:// servers are supported");
  } else if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new Error("The address must start with https://");
  }

  // Servers are always at the root of their host.
  url.username = "";
  url.password = "";
  url.pathname = "/";
  url.search = "";
  url.hash = "";

  return url;
}

async function fetchLatestVersions(httpGet, serverUrl) {
  const latestVersionsUrl = new URL("apps-latest-versions", serverUrl);
  latestVersionsUrl.searchParams.set("distribution", "web");
  return await httpGet(latestVersionsUrl.toString());
}

function getHeader(response, name) {
  const lowerName = name.toLowerCase();
  for (const [key, value] of Object.entries(response.headers ?? {})) {
    if (key.toLowerCase() === lowerName) {
      return value;
    }
  }
  return null;
}

function parseMajor(version) {
  const match = /^v?(\d+)\.\d+\.\d+/.exec(version);
  return match === null ? null : parseInt(match[1], 10);
}

function describeError(error) {
  // Node's fetch hides the useful part (ECONNREFUSED and the like) in `cause`.
  const cause = error?.cause;
  return String(cause?.code ?? cause?.message ?? error?.message ?? error);
}
