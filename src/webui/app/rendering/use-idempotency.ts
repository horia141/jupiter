import { useEffect, useState } from "react";

export function useIdempotencyKey(storageKey: string) {
  const [key, setKey] = useState<string>("");

  useEffect(() => {
    // Reuse the same key across retries/reloads until success
    let k = window.sessionStorage.getItem(storageKey);
    if (!k) {
      k = crypto.randomUUID(); // modern browsers
      window.sessionStorage.setItem(storageKey, k);
    }
    setKey(k);
  }, [storageKey]);

  const clear = () => window.sessionStorage.removeItem(storageKey);
  return { key, clear };
}
