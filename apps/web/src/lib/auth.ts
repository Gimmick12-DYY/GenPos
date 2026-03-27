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
  return "API 返回错误，请稍后重试";
}

async function requestDevToken(): Promise<{ access_token: string; merchant_id: string }> {
  const url = `${API_BASE}/auth/dev-token`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  if (res.ok) {
    const data = await res.json();
    return { access_token: data.access_token, merchant_id: data.merchant_id };
  }
  const err = await res.json().catch(async () => {
    const text = await res.text().catch(() => "");
    return { _status: res.status, _body: text.slice(0, 200) };
  });
  const detail = "detail" in err ? err.detail : ("_body" in err ? (err as { _body: string })._body || `HTTP ${(err as { _status: number })._status}` : `HTTP ${res.status}`);
  throw { status: res.status, detail: formatApiError(detail), isNoMerchant: res.status === 404 && String(detail).toLowerCase().includes("merchant") };
}

export async function ensureAuth(options?: {
  forceRefresh?: boolean;
}): Promise<{ token: string; merchantId: string }> {
  if (!options?.forceRefresh) {
    const token = getToken();
    const merchantId = getMerchantId();
    if (token && merchantId) return { token, merchantId };
  } else {
    clearAuth();
  }

  try {
    const data = await requestDevToken();
    setAuth(data.access_token, data.merchant_id);
    return { token: data.access_token, merchantId: data.merchant_id };
  } catch (e: unknown) {
    const noMerchant = typeof e === "object" && e !== null && "isNoMerchant" in e && (e as { isNoMerchant: boolean }).isNoMerchant;
    const detail = typeof e === "object" && e !== null && "detail" in e ? String((e as { detail: string }).detail) : null;
    const networkError = e instanceof Error && (/fetch|network|Failed to fetch/i.test(e.message) || e.name === "TypeError");

    if (networkError) {
      throw new Error(
        "无法连接后端。请检查：1) Vercel 环境变量 NEXT_PUBLIC_API_URL 指向 Railway API 地址（需含 /api/v1）；2) Railway 上 CORS_ORIGINS 包含当前前端地址；3) API 服务已启动。"
      );
    }
    if (noMerchant) {
      try {
        const bootstrapRes = await fetch(`${API_BASE}/auth/bootstrap`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });
        if (bootstrapRes.ok) {
          const data = await requestDevToken();
          setAuth(data.access_token, data.merchant_id);
          return { token: data.access_token, merchantId: data.merchant_id };
        }
      } catch {
        /* ignore bootstrap failure, throw clear message below */
      }
      throw new Error("数据库中尚无商户。已自动尝试创建；若仍失败请检查 API 日志并确认已执行数据库迁移（alembic upgrade head）。");
    }
    throw new Error(detail ?? "无法连接后端");
  }
}
