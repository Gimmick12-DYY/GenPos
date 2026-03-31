"use client";

import { useState, useEffect, useCallback } from "react";
import { ClipboardCheck, Filter, Search } from "lucide-react";
import { NotePackageCard } from "@/components/note-package-card";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { ensureAuth, getMerchantId } from "@/lib/auth";

type TabKey = "pending" | "approved" | "rejected";

interface QueueItem {
  id: string;
  style_family?: string | null;
  ranking_score?: number | null;
  compliance_status: string;
  review_status: string;
}

interface PagedQueue {
  items: QueueItem[];
  total: number;
}

function complianceToCardStatus(
  s: string
): "passed" | "failed" | "pending" | "review_needed" | "draft" {
  if (s === "passed") return "passed";
  if (s === "failed") return "failed";
  if (s === "review_needed") return "review_needed";
  if (s === "pending") return "pending";
  return "draft";
}

function cardTitle(pkg: QueueItem): string {
  return pkg.style_family ? `笔记 · ${pkg.style_family}` : "笔记方案";
}

export default function ReviewPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("pending");
  const [authReady, setAuthReady] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [counts, setCounts] = useState({ pending: 0, approved: 0, rejected: 0 });
  const [items, setItems] = useState<QueueItem[]>([]);
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

  const loadCounts = useCallback(async (merchantId: string) => {
    try {
      const [p, a, r] = await Promise.all([
        api.get<PagedQueue>(
          `/review/queue?merchant_id=${merchantId}&limit=1&offset=0`
        ),
        api.get<PagedQueue>(
          `/note-packages?merchant_id=${merchantId}&review_status=approved&limit=1&offset=0&sort=ranking`
        ),
        api.get<PagedQueue>(
          `/note-packages?merchant_id=${merchantId}&review_status=rejected&limit=1&offset=0&sort=recent`
        ),
      ]);
      setCounts({
        pending: p.total,
        approved: a.total,
        rejected: r.total,
      });
    } catch {
      /* counts non-fatal */
    }
  }, []);

  const loadTab = useCallback(
    async (tab: TabKey, merchantId: string) => {
      setLoading(true);
      setListError(null);
      try {
        if (tab === "pending") {
          const res = await api.get<PagedQueue>(
            `/review/queue?merchant_id=${merchantId}&limit=60&offset=0`
          );
          setItems(res.items);
          setTotal(res.total);
        } else {
          const status = tab === "approved" ? "approved" : "rejected";
          const sort = tab === "approved" ? "ranking" : "recent";
          const res = await api.get<PagedQueue>(
            `/note-packages?merchant_id=${merchantId}&review_status=${status}&limit=60&offset=0&sort=${sort}`
          );
          setItems(res.items);
          setTotal(res.total);
        }
      } catch (e) {
        setListError(
          e instanceof Error ? e.message : "加载失败"
        );
        setItems([]);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    if (!authReady) return;
    const merchantId = getMerchantId();
    if (!merchantId) return;
    void loadCounts(merchantId);
    void loadTab(activeTab, merchantId);
  }, [authReady, activeTab, loadCounts, loadTab]);

  async function handleApprove(id: string) {
    const merchantId = getMerchantId();
    if (!merchantId) return;
    try {
      await api.post(`/review/${id}/approve`, {});
      await loadCounts(merchantId);
      await loadTab(activeTab, merchantId);
    } catch (e) {
      alert(e instanceof Error ? e.message : "操作失败");
    }
  }

  async function handleReject(id: string) {
    const reason =
      window.prompt("拒绝原因（必填）：", "未填写") ?? "未填写";
    if (!reason.trim()) return;
    const merchantId = getMerchantId();
    if (!merchantId) return;
    try {
      await api.post(`/review/${id}/reject`, { reason: reason.trim() });
      await loadCounts(merchantId);
      await loadTab(activeTab, merchantId);
    } catch (e) {
      alert(e instanceof Error ? e.message : "操作失败");
    }
  }

  const tabs: { key: TabKey; label: string; count: number }[] = [
    { key: "pending", label: "待审核", count: counts.pending },
    { key: "approved", label: "已通过", count: counts.approved },
    { key: "rejected", label: "已拒绝", count: counts.rejected },
  ];

  const q = search.trim().toLowerCase();
  const filtered = q
    ? items.filter((it) => {
        const t = cardTitle(it).toLowerCase();
        const id = it.id.toLowerCase();
        return t.includes(q) || id.includes(q);
      })
    : items;

  if (authError && !authReady) {
    return (
      <div className="mx-auto max-w-7xl p-6 lg:p-8">
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center text-sm text-red-800">
          {authError}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl p-6 lg:p-8">
      <div className="mb-8 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-light shadow-sm">
          <ClipboardCheck className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-stone-900">待审核</h1>
          <p className="text-sm text-stone-500">
            审核 AI 生成的笔记方案，确保符合品牌规范
          </p>
        </div>
      </div>

      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex gap-1 rounded-lg bg-stone-100 p-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveTab(tab.key)}
              className={cn(
                "flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-all",
                activeTab === tab.key
                  ? "bg-surface-raised text-stone-900 shadow-sm"
                  : "text-stone-500 hover:text-stone-700"
              )}
            >
              {tab.label}
              <span
                className={cn(
                  "flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-xs",
                  activeTab === tab.key
                    ? "bg-primary/10 text-primary-dark"
                    : "bg-stone-200 text-stone-500"
                )}
              >
                {tab.count}
              </span>
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="搜索笔记…"
              className="h-9 w-60 rounded-lg border border-stone-300 bg-white pl-9 pr-3 text-sm placeholder:text-stone-400 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
          </div>
          <button
            type="button"
            className="flex h-9 items-center gap-1.5 rounded-lg border border-stone-300 bg-white px-3 text-sm text-stone-600 transition-colors hover:bg-stone-50"
            aria-hidden
          >
            <Filter className="h-3.5 w-3.5" />
            筛选
          </button>
        </div>
      </div>

      {listError && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          {listError}
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-80 animate-pulse rounded-xl border border-stone-200 bg-stone-100"
            />
          ))}
        </div>
      ) : activeTab === "pending" ? (
        filtered.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-surface-raised py-16 text-center text-stone-500">
            <p>暂无待审核的笔记</p>
            <p className="mt-1 text-sm">
              在「一键生成」或「AI对话」中创建内容后会出现在这里
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {filtered.map((item) => (
              <NotePackageCard
                key={item.id}
                title={cardTitle(item)}
                score={
                  item.ranking_score != null
                    ? Math.round(item.ranking_score)
                    : undefined
                }
                styleFamily={item.style_family ?? undefined}
                complianceStatus={complianceToCardStatus(
                  item.compliance_status
                )}
                onApprove={() => handleApprove(item.id)}
                onReject={() => handleReject(item.id)}
              />
            ))}
          </div>
        )
      ) : filtered.length === 0 ? (
        <div className="rounded-xl border border-stone-200 bg-surface-raised p-12 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-stone-50">
            <ClipboardCheck className="h-8 w-8 text-stone-400" />
          </div>
          <h3 className="text-lg font-semibold text-stone-900">
            {activeTab === "approved"
              ? "暂无已通过记录"
              : "暂无已拒绝记录"}
          </h3>
          <p className="mt-1 text-sm text-stone-500">共 {total} 条（全库）</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((item) => (
            <NotePackageCard
              key={item.id}
              title={cardTitle(item)}
              score={
                item.ranking_score != null
                  ? Math.round(item.ranking_score)
                  : undefined
              }
              styleFamily={item.style_family ?? undefined}
              complianceStatus={complianceToCardStatus(item.compliance_status)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
