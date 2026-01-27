const getEnv = (key: string, fallback?: string): string => {
  // 1. Runtime Injection (Docker/Azure/K8s)
  if (typeof window !== "undefined" && (window as any).__ENV?.[key]) {
    return (window as any).__ENV[key];
  }
  // 2. Build-time / Dev fallback
  return fallback || "";
};

// We define the fallback here so we don't have to repeat it in components
const rawUrl = getEnv("NEXT_PUBLIC_API_URL", process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000");

// Safety: Remove trailing slash if present to avoid "http://url//api"
export const API_URL = rawUrl.replace(/\/$/, "");