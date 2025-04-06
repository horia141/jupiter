export function newURLParams(
  query: URLSearchParams,
  key: string,
  value: string,
): URLSearchParams {
  const newQuery = new URLSearchParams(query.toString());
  newQuery.set(key, value);
  return newQuery;
}
