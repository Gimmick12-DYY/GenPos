import { ensureAuth, getToken } from "./auth";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function request<T>(
  path: string,
  options?: RequestInit,
  _retriedAfter401 = false
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options?.headers,
  };
  const token = getToken();
  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(url, {
    ...options,
    headers,
  });
  if (!res.ok) {
    if (
      res.status === 401 &&
      !_retriedAfter401 &&
      !path.startsWith("/auth/")
    ) {
      try {
        await ensureAuth({ forceRefresh: true });
        return request<T>(path, options, true);
      } catch {
        /* fall through to surface API error */
      }
    }
    const err = await res.json().catch(() => ({}));
    const detail = (err as { detail?: unknown }).detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail) && detail[0]?.msg
          ? detail.map((d: { msg: string }) => d.msg).join("; ")
          : `API error: ${res.status} ${res.statusText}`;
    throw new Error(message);
  }
  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  delete: (path: string) => request(path, { method: "DELETE" }),
};
