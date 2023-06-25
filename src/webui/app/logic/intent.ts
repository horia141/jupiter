export function makeIntent<T>(intent: string, args?: T): string {
  if (args !== undefined) {
    return `${intent}:${JSON.stringify(args)}`;
  } else {
    return intent;
  }
}

const INTENT_RE = /^([a-z][a-z-]+)(:(.+))?$/;

export function getIntent<T>(serialized: string): { intent: string; args?: T } {
  const res = serialized.match(INTENT_RE);
  if (!res) {
    throw Error("Can't parse intent");
  } else if (res.length !== 4) {
    throw Error("Can't parse intent");
  }
  const intent = res[1];
  const args_raw = res[3];
  let args = undefined;
  if (args_raw !== undefined) {
    args = JSON.parse(args_raw) as T;
  }
  return { intent, args };
}
