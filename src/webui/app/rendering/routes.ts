export const WORKSPACE_ROUTE_MATCHER = /\/app\/workspace\/(.*)/;
const TRUNK_ROUTE_MATCHER = /\/app\/workspace\/([^/]*)(\/.*)?/;

export function extractTrunkFromPath(path: string): string {
  const match = path.match(TRUNK_ROUTE_MATCHER);
  if (match !== null) {
    return `/app/workspace/${match[1]}`;
  }

  if (path === "/app/workspace") {
    return path;
  }

  return null as unknown as string;
  // throw new Error(`Could not extract trunk from path: ${path}`);
}

const STRICT_TRUNK_ROUTE_MATCHER = /\/app\/workspace\/([^/]*)/;
const BRANCH_ROUTE_MATCHER = /\/app\/workspace\/([^/]*)\/([^/]*)(\/.*)?/;

export function extractBranchFromPath(path: string): string {
  const match = path.match(BRANCH_ROUTE_MATCHER);
  if (match !== null) {
    return `/app/workspace/${match[1]}/${match[2]}`;
  }

  const strictMatch = path.match(STRICT_TRUNK_ROUTE_MATCHER);
  if (strictMatch !== null) {
    return `/app/workspace/${strictMatch[1]}`;
  }

  return null as unknown as string;
  // throw new Error(`Could not extract branch from path: ${path}`);
}
