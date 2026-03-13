const TOKEN_KEY = "genpos_token";
const MERCHANT_KEY = "genpos_merchant_id";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getMerchantId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(MERCHANT_KEY);
}

export function setAuth(token: string, merchantId: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(MERCHANT_KEY, merchantId);
}

export function clearAuth(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(MERCHANT_KEY);
}

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function formatApiError(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return detail.map((d) => d.msg).join("; ");
  if (typeof detail === "object" && detail && "detail" in detail) return formatApiError((detail as { detail: unknown }).detail);
  return "Failed to get dev token";
}

export async function ensureAuth(): Promise<{ token: string; merchantId: string }> {
  const token = getToken();
  const merchantId = getMerchantId();
  if (token && merchantId) return { token, merchantId };

  const url = `${API_BASE}/auth/dev-token`;
  let res: Response;
  try {
    res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Network error";
    throw new Error(
      `无法连接后端：${msg}。请检查 Vercel 环境变量 NEXT_PUBLIC_API_URL 是否指向 Railway API 地址，且 API 服务已启动。`
    );
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = "detail" in err ? err.detail : "Failed to get dev token";
    throw new Error(formatApiError(detail));
  }
  const data = await res.json();
  setAuth(data.access_token, data.merchant_id);
  return { token: data.access_token, merchantId: data.merchant_id };
}
