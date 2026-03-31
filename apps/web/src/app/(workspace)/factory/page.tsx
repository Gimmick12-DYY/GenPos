"use client";

import { useState, useEffect, useMemo } from "react";
import { Factory, Search, MoreHorizontal } from "lucide-react";
import { PageHeader, PageShell } from "@/components/layout/page-shell";
import { StatusBadge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { ensureAuth, getMerchantId } from "@/lib/auth";

interface NoteRow {
  id: string;
  style_family?: string | null;
  ranking_score?: number | null;
  compliance_status: string;
  review_status: string;
  product_name?: string | null;
  created_at: string;
}

interface Paged {
  items: NoteRow[];
  total: number;
}

function rowBadge(
  review: string,
  compliance: string
): "passed" | "failed" | "pending" | "review_needed" | "draft" {
  if (review === "approved") return "passed";
  if (review === "rejected") return "failed";
  if (compliance === "failed") return "failed";
  if (compliance === "review_needed") return "review_needed";
  if (compliance === "passed") return "passed";
  return "pending";
}

function titleFromRow(row: NoteRow): string {
  return row.style_family ? `笔记 · ${row.style_family}` : "笔记方案";
}

export default function FactoryPage() {
  const [authReady, setAuthReady] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [rows, setRows] = useState<NoteRow[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [listError, setListError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    ensureAuth()
      .then(() => setAuthReady(true))
      .catch((e) =>
        setAuthError(e instanceof Error ? e.message : "认证失败")
      );
  }, []);

  useEffect(() => {
    if (!authReady) return;
    const merchantId = getMerchantId();
    if (!merchantId) return;
    setLoading(true);
    setListError(null);
    api
      .get<Paged>(
        `/note-packages?merchant_id=${merchantId}&limit=100&offset=0&sort=recent`
      )
      .then((res) => {
        setRows(
          res.items.map((it) => ({
            ...it,
            created_at:
              typeof it.created_at === "string"
                ? it.created_at
                : String(it.created_at),
          }))
        );
        setTotal(res.total);
      })
      .catch((e) =>
        setListError(e instanceof Error ? e.message : "加载失败")
      )
      .finally(() => setLoading(false));
  }, [authReady]);

  const q = search.trim().toLowerCase();
  const filtered = useMemo(() => {
    if (!q) return rows;
    return rows.filter((r) => {
      const title = titleFromRow(r).toLowerCase();
      const prod = (r.product_name ?? "").toLowerCase();
      const id = r.id.toLowerCase();
      return title.includes(q) || prod.includes(q) || id.includes(q);
    });
  }, [rows, q]);

  const formatDate = (iso: string) => {
    try {
      return new Date(iso).toLocaleDateString("zh-CN");
    } catch {
      return iso.slice(0, 10);
    }
  };

  if (authError && !authReady) {
    return (
      <PageShell>
        <div className="rounded-2xl border border-red-200/80 bg-red-50 p-8 text-center text-sm text-red-900 shadow-sm">
          {authError}
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageHeader
        icon={Factory}
        title="内容工厂"
        description={`查看和管理所有生成的笔记内容（共 ${total} 条）`}
      />

      <div className="mb-6 flex items-center gap-3">
        <div className="relative max-w-md flex-1">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="搜索标题、产品、编号…"
            className="input-surface h-10 w-full pl-10 pr-3 text-sm"
          />
        </div>
      </div>

      {listError && (
        <div className="mb-4 rounded-2xl border border-red-200/80 bg-red-50 px-4 py-3 text-sm text-red-900 shadow-sm">
          {listError}
        </div>
      )}

      {loading ? (
        <div className="h-64 animate-pulse rounded-2xl border border-stone-200/80 bg-stone-100/80" />
      ) : filtered.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-stone-300/80 bg-surface-raised py-16 text-center text-stone-500 shadow-sm">
          <p>{rows.length === 0 ? "还没有生成的笔记包" : "没有匹配的结果"}</p>
          {!rows.length && (
            <p className="mt-1 text-sm">在「一键生成」中创建内容后会出现在这里</p>
          )}
        </div>
      ) : (
        <div className="overflow-hidden rounded-2xl border border-stone-200/80 bg-surface-raised shadow-sm">
          <table className="w-full">
            <thead>
              <tr className="border-b border-stone-200 bg-stone-50/80">
                <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                  编号
                </th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                  标题
                </th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                  产品
                </th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                  风格
                </th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                  评分
                </th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                  状态
                </th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                  创建日期
                </th>
                <th className="w-10 px-3 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {filtered.map((item) => (
                <tr
                  key={item.id}
                  className="transition-colors hover:bg-stone-50/50"
                >
                  <td className="px-5 py-3.5 text-xs font-mono text-stone-400">
                    {item.id.slice(0, 8)}…
                  </td>
                  <td className="px-5 py-3.5 text-sm font-medium text-stone-900">
                    {titleFromRow(item)}
                  </td>
                  <td className="px-5 py-3.5 text-sm text-stone-600">
                    {item.product_name ?? "—"}
                  </td>
                  <td className="px-5 py-3.5">
                    {item.style_family ? (
                      <span className="inline-block rounded-md bg-stone-100 px-2 py-0.5 text-xs text-stone-600">
                        {item.style_family}
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td className="px-5 py-3.5 text-sm font-semibold text-stone-900">
                    {item.ranking_score != null
                      ? Math.round(item.ranking_score * 100) / 100
                      : "—"}
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge
                      status={rowBadge(
                        item.review_status,
                        item.compliance_status
                      )}
                    />
                  </td>
                  <td className="px-5 py-3.5 text-sm text-stone-500">
                    {formatDate(item.created_at)}
                  </td>
                  <td className="px-3 py-3.5">
                    <button
                      type="button"
                      className="rounded p-1 text-stone-400 hover:bg-stone-100 hover:text-stone-600"
                      aria-label="更多"
                    >
                      <MoreHorizontal className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </PageShell>
  );
}
