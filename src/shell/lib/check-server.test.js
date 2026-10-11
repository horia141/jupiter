import { describe, expect, it } from "vitest";

import { checkServer, normalizeServerUrl } from "./check-server.js";

const VERSION = "1.3.3";

// A fake server: maps a URL to the response httpGet should give, or to an
// Error it should throw.
function fakeHttpGet(responses) {
  const calls = [];
  const httpGet = async (url) => {
    calls.push(url);
    const response = responses[url];
    if (response === undefined) {
      throw new Error(`unexpected request to ${url}`);
    }
    if (response instanceof Error) {
      throw response;
    }
    return response;
  };
  return { httpGet, calls };
}

function thriveAt(origin, version = VERSION) {
  return {
    [`${origin}/apps-latest-versions?distribution=web`]: {
      status: 302,
      headers: { location: "/app/workspace", "x-jupiter-version": version },
    },
  };
}

describe("normalizeServerUrl", () => {
  it("assumes https for a bare address", () => {
    expect(
      normalizeServerUrl("thrive-test.com", { allowHttp: false }).toString(),
    ).toBe("https://thrive-test.com/");
  });

  it("assumes http for a bare local address when http is allowed", () => {
    expect(
      normalizeServerUrl("localhost:27492", { allowHttp: true }).toString(),
    ).toBe("http://localhost:27492/");
  });

  it("assumes https for a bare local address when http is not allowed", () => {
    expect(
      normalizeServerUrl("localhost:27492", { allowHttp: false }).toString(),
    ).toBe("https://localhost:27492/");
  });

  it("rejects http unless allowed", () => {
    expect(() =>
      normalizeServerUrl("http://thrive-test.com", { allowHttp: false }),
    ).toThrow("Only https:// servers are supported");
    expect(
      normalizeServerUrl("http://thrive-test.com", {
        allowHttp: true,
      }).toString(),
    ).toBe("http://thrive-test.com/");
  });

  it("rejects other schemes", () => {
    expect(() =>
      normalizeServerUrl("ftp://thrive-test.com", { allowHttp: true }),
    ).toThrow("The address must start with https://");
  });

  it("rejects an empty address", () => {
    expect(() => normalizeServerUrl("   ", { allowHttp: false })).toThrow(
      "Please enter a server address",
    );
  });

  it("strips quotes, credentials, paths, queries and fragments", () => {
    expect(
      normalizeServerUrl(
        "  'https://me:secret@thrive-test.com:8443/app/workspace?x=1#y'  ",
        { allowHttp: false },
      ).toString(),
    ).toBe("https://thrive-test.com:8443/");
  });
});

describe("checkServer", () => {
  it("accepts a compatible server", async () => {
    const { httpGet } = fakeHttpGet(thriveAt("https://thrive-test.com"));
    expect(
      await checkServer("thrive-test.com", {
        httpGet,
        allowHttp: false,
        clientVersion: VERSION,
      }),
    ).toEqual({ result: "ok", serverUrl: "https://thrive-test.com/" });
  });

  it("follows one http to https redirect", async () => {
    const { httpGet, calls } = fakeHttpGet({
      "http://thrive-test.com/apps-latest-versions?distribution=web": {
        status: 301,
        headers: {
          Location:
            "https://thrive-test.com/apps-latest-versions?distribution=web",
        },
      },
      ...thriveAt("https://thrive-test.com"),
    });
    const res = await checkServer("http://thrive-test.com", {
      httpGet,
      allowHttp: true,
      clientVersion: VERSION,
    });
    expect(res).toEqual({ result: "ok", serverUrl: "http://thrive-test.com/" });
    expect(calls).toHaveLength(2);
  });

  it("rejects a server without the version header", async () => {
    const { httpGet } = fakeHttpGet({
      "https://example.com/apps-latest-versions?distribution=web": {
        status: 404,
        headers: {},
      },
    });
    expect(
      await checkServer("example.com", {
        httpGet,
        allowHttp: false,
        clientVersion: VERSION,
      }),
    ).toEqual({
      result: "error",
      errorMsg: "The server doesn't appear to be a Thrive server",
    });
  });

  it("rejects a server with an unparseable version", async () => {
    const { httpGet } = fakeHttpGet(
      thriveAt("https://thrive-test.com", "banana"),
    );
    expect(
      await checkServer("thrive-test.com", {
        httpGet,
        allowHttp: false,
        clientVersion: VERSION,
      }),
    ).toEqual({
      result: "error",
      errorMsg: "The server reports an unexpected version: banana",
    });
  });

  it("rejects a server on another major version", async () => {
    const { httpGet } = fakeHttpGet(
      thriveAt("https://thrive-test.com", "2.0.0"),
    );
    expect(
      await checkServer("thrive-test.com", {
        httpGet,
        allowHttp: false,
        clientVersion: VERSION,
      }),
    ).toEqual({
      result: "error",
      errorMsg:
        "This app's version 1.3.3 is incompatible with the server's 2.0.0",
    });
  });

  it("accepts a server on another minor version", async () => {
    const { httpGet } = fakeHttpGet(
      thriveAt("https://thrive-test.com", "1.9.0"),
    );
    const res = await checkServer("thrive-test.com", {
      httpGet,
      allowHttp: false,
      clientVersion: VERSION,
    });
    expect(res.result).toBe("ok");
  });

  it("reports an unreachable server with the underlying cause", async () => {
    const error = new TypeError("fetch failed");
    error.cause = { code: "ECONNREFUSED" };
    const { httpGet } = fakeHttpGet({
      "https://thrive-test.com/apps-latest-versions?distribution=web": error,
    });
    expect(
      await checkServer("thrive-test.com", {
        httpGet,
        allowHttp: false,
        clientVersion: VERSION,
      }),
    ).toEqual({
      result: "error",
      errorMsg: "Could not reach the server: ECONNREFUSED",
    });
  });

  it("does not make a request for an invalid address", async () => {
    const { httpGet, calls } = fakeHttpGet({});
    const res = await checkServer("http://thrive-test.com", {
      httpGet,
      allowHttp: false,
      clientVersion: VERSION,
    });
    expect(res.result).toBe("error");
    expect(calls).toHaveLength(0);
  });
});
