export function compareIsKey(a: boolean, b: boolean) {
  if (a === b) {
    return 0;
  }
  return a ? -1 : 1;
}
