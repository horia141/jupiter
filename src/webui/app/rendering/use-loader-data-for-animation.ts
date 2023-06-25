import type { SerializeFrom } from "@remix-run/node";
import { useLoaderData } from "@remix-run/react";
import { useEffect, useRef } from "react";

export function useLoaderDataSafeForAnimation<T>(): SerializeFrom<T> {
  const lastData = useRef({});
  const data = useLoaderData<T>() || lastData.current;

  useEffect(() => {
    if (data) lastData.current = data;
  }, [data]);

  return data as SerializeFrom<T>;
}
