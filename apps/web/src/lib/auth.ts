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

export async function ensureAuth(): Promise<{ token: string; merchantId: string }> {
  const token = getToken();
  const merchantId = getMerchantId();
  if (token && merchantId) return { token, merchantId };

  const res = await fetch(`${API_BASE}/auth/dev-token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to get dev token");
  }
  const data = await res.json();
  setAuth(data.access_token, data.merchant_id);
  return { token: data.access_token, merchantId: data.merchant_id };
}
