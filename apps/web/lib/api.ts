export const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function authHeaders(extra: HeadersInit = {}): HeadersInit {
  return {
    Authorization: `Bearer ${localStorage.getItem("mf_token") || ""}`,
    "X-Organization-ID": localStorage.getItem("mf_org") || "",
    ...extra,
  };
}

export async function apiJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API}${path}`, init);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload?.detail;
    throw new Error(
      typeof detail === "string" ? detail : detail?.message || payload?.error?.message || "Request failed",
    );
  }
  return payload as T;
}
