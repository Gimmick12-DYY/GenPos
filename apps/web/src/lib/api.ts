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
  /** Multipart upload; do not set Content-Type (browser sets boundary). */
  postForm: async <T>(path: string, formData: FormData): Promise<T> => {
    const url = `${API_BASE}${path}`;
    const headers: HeadersInit = {};
    const token = getToken();
    if (token) {
      (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
    }
    const res = await fetch(url, { method: "POST", headers, body: formData });
    if (!res.ok) {
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
  },
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};

/** POST SSE (text/event-stream); parses `data: {...}` lines (BL-101). */
export async function postSse(
  path: string,
  body: unknown,
  onData: (obj: Record<string, unknown>) => void
): Promise<void> {
  const url = `${API_BASE}${path}`;
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    Accept: "text/event-stream",
  };
  const token = getToken();
  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(url, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    if (res.status === 401) {
      try {
        await ensureAuth({ forceRefresh: true });
        return postSse(path, body, onData);
      } catch {
        /* fall through */
      }
    }
    const err = await res.json().catch(() => ({}));
    const detail = (err as { detail?: unknown }).detail;
    const message =
      typeof detail === "string"
        ? detail
        : `API error: ${res.status} ${res.statusText}`;
    throw new Error(message);
  }
  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const block of parts) {
      for (const line of block.split("\n")) {
        const t = line.trim();
        if (!t.startsWith("data:")) continue;
        const raw = t.slice(5).trim();
        try {
          const obj = JSON.parse(raw) as Record<string, unknown>;
          onData(obj);
        } catch {
          /* ignore malformed chunk */
        }
      }
    }
  }
}
