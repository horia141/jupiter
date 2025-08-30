export function newURLParams(
  query: URLSearchParams,
  key: string,
  value: string,
  ...rest: string[]
): URLSearchParams {
  const newQuery = new URLSearchParams(query.toString());
  newQuery.set(key, value);
  for (let i = 0; i < rest.length; i += 2) {
    newQuery.set(rest[i], rest[i + 1]);
  }
  return newQuery;
}
