import { useState, useEffect } from "react";
import { useHydrated } from "~/rendering/use-hidrated";

interface ClientOnlyProps {
  children: React.ReactNode | (() => React.ReactNode);
  fallback?: React.ReactNode;
}

export function ClientOnly({ children, fallback = null }: ClientOnlyProps) {
  const hydrated = useHydrated();

  if (!hydrated) {
    return <>{fallback}</>;
  }

  return <>{typeof children === "function" ? children() : children}</>;
}
