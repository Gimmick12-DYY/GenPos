"use client";

import { useState, useEffect, useCallback } from "react";
import { ClipboardCheck, Filter, LayoutGrid, List, Search, X } from "lucide-react";
import { NotePackageCard } from "@/components/note-package-card";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { ensureAuth, getMerchantId } from "@/lib/auth";

type TabKey = "pending" | "approved" | "rejected";
type LayoutMode = "list" | "kanban";

interface QueueItem {
  id: string;
  style_family?: string | null;
  ranking_score?: number | null;
  compliance_status: string;
  review_status: string;
  cover_url?: string | null;
}

interface PagedQueue {
  items: QueueItem[];
  total: number;
}

interface DetailTitleRow {
  id: string;
  asset_role: string;
  content: string;
}

interface NoteDetail {
  id: string;
  text_assets: DetailTitleRow[];
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
  const [layout, setLayout] = useState<LayoutMode>("list");
  const [activeTab, setActiveTab] = useState<TabKey>("pending");
  const [authReady, setAuthReady] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [counts, setCounts] = useState({
    pending: 0,
    approved: 0,
    rejected: 0,
    queued: 0,
    live: 0,
  });
  const [items, setItems] = useState<QueueItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [listError, setListError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [board, setBoard] = useState<{
    pending: QueueItem[];
    approved: QueueItem[];
    queued: QueueItem[];
    live: QueueItem[];
  } | null>(null);
  const [boardLoading, setBoardLoading] = useState(false);
  const [detailId, setDetailId] = useState<string | null>(null);
  const [detail, setDetail] = useState<NoteDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [editTitleId, setEditTitleId] = useState<string | null>(null);
  const [editTitleText, setEditTitleText] = useState("");

  useEffect(() => {
    ensureAuth()
      .then(() => setAuthReady(true))
      .catch((e) =>
        setAuthError(e instanceof Error ? e.message : "认证失败")
      );
  }, []);

  const loadCounts = useCallback(async (merchantId: string) => {
    try {
      const [p, a, r, q, l] = await Promise.all([
        api.get<PagedQueue>(
          `/review/queue?merchant_id=${merchantId}&limit=1&offset=0`
        ),
        api.get<PagedQueue>(
          `/note-packages?merchant_id=${merchantId}&review_status=approved&limit=1&offset=0&sort=ranking`
        ),
        api.get<PagedQueue>(
          `/note-packages?merchant_id=${merchantId}&review_status=rejected&limit=1&offset=0&sort=recent`
        ),
        api.get<PagedQueue>(
          `/note-packages?merchant_id=${merchantId}&review_status=queued&limit=1&offset=0&sort=recent`
        ),
        api.get<PagedQueue>(
          `/note-packages?merchant_id=${merchantId}&review_status=live&limit=1&offset=0&sort=recent`
        ),
      ]);
      setCounts({
        pending: p.total,
        approved: a.total,
        rejected: r.total,
        queued: q.total,
        live: l.total,
      });
    } catch {
      /* non-fatal */
    }
  }, []);

  const loadKanban = useCallback(async (merchantId: string) => {
    setBoardLoading(true);
    setListError(null);
    try {
      const [p, a, q, l] = await Promise.all([
        api.get<PagedQueue>(
          `/review/queue?merchant_id=${merchantId}&limit=40&offset=0`
        ),
        api.get<PagedQueue>(
          `/note-packages?merchant_id=${merchantId}&review_status=approved&limit=40&offset=0&sort=ranking`
        ),
        api.get<PagedQueue>(
          `/note-packages?merchant_id=${merchantId}&review_status=queued&limit=40&offset=0&sort=recent`
        ),
        api.get<PagedQueue>(
          `/note-packages?merchant_id=${merchantId}&review_status=live&limit=40&offset=0&sort=recent`
        ),
      ]);
      setBoard({
        pending: p.items,
        approved: a.items,
        queued: q.items,
        live: l.items,
      });
    } catch (e) {
      setListError(e instanceof Error ? e.message : "看板加载失败");
      setBoard(null);
    } finally {
      setBoardLoading(false);
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
        setListError(e instanceof Error ? e.message : "加载失败");
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
    if (layout === "list") void loadTab(activeTab, merchantId);
    else void loadKanban(merchantId);
  }, [authReady, activeTab, layout, loadCounts, loadKanban, loadTab]);

  async function refreshAll() {
    const merchantId = getMerchantId();
    if (!merchantId) return;
    await loadCounts(merchantId);
    if (layout === "list") await loadTab(activeTab, merchantId);
    else await loadKanban(merchantId);
  }

  async function handleApprove(id: string) {
    const merchantId = getMerchantId();
    if (!merchantId) return;
    try {
      await api.post(`/review/${id}/approve`, {});
      await refreshAll();
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
      await refreshAll();
    } catch (e) {
      alert(e instanceof Error ? e.message : "操作失败");
    }
  }

  async function patchStatus(id: string, review_status: string) {
    try {
      await api.patch(`/note-packages/${id}`, { review_status });
      await refreshAll();
    } catch (e) {
      alert(e instanceof Error ? e.message : "更新失败");
    }
  }

  useEffect(() => {
    if (!detailId || !authReady) {
      setDetail(null);
      return;
    }
    setDetailLoading(true);
    api
      .get<NoteDetail>(`/note-packages/${detailId}`)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setDetailLoading(false));
  }, [detailId, authReady]);

  async function saveTitleAsset() {
    if (!editTitleId || !detailId) return;
    try {
      await api.patch(`/text-assets/${editTitleId}`, {
        content: editTitleText,
      });
      setEditTitleId(null);
      const d = await api.get<NoteDetail>(`/note-packages/${detailId}`);
      setDetail(d);
    } catch (e) {
      alert(e instanceof Error ? e.message : "保存失败");
    }
  }

  const tabs: { key: TabKey; label: string; count: number }[] = [
    { key: "pending", label: "待审核", count: counts.pending },
    { key: "approved", label: "已通过", count: counts.approved },
    { key: "rejected", label: "已拒绝", count: counts.rejected },
  ];

  const q = search.trim().toLowerCase();
  const filterItems = (arr: QueueItem[]) =>
    q
      ? arr.filter((it) => {
          const t = cardTitle(it).toLowerCase();
          const id = it.id.toLowerCase();
          return t.includes(q) || id.includes(q);
        })
      : arr;

  const filtered = filterItems(items);

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
      <div className="mb-8 flex flex-wrap items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-light shadow-sm">
          <ClipboardCheck className="h-5 w-5 text-white" />
        </div>
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold text-stone-900">待审核</h1>
          <p className="text-sm text-stone-500">
            审核 AI 生成的笔记方案；看板覆盖待审 → 通过 → 排期 → 发布
          </p>
        </div>
        <div className="flex rounded-lg bg-stone-100 p-0.5">
          <button
            type="button"
            onClick={() => setLayout("list")}
            className={cn(
              "flex items-center gap-1 rounded-md px-3 py-1.5 text-sm font-medium",
              layout === "list"
                ? "bg-surface-raised text-stone-900 shadow-sm"
                : "text-stone-500",
            )}
          >
            <List className="h-4 w-4" />
            列表
          </button>
          <button
            type="button"
            onClick={() => setLayout("kanban")}
            className={cn(
              "flex items-center gap-1 rounded-md px-3 py-1.5 text-sm font-medium",
              layout === "kanban"
                ? "bg-surface-raised text-stone-900 shadow-sm"
                : "text-stone-500",
            )}
          >
            <LayoutGrid className="h-4 w-4" />
            看板
          </button>
        </div>
      </div>

      {layout === "list" && (
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
                    : "text-stone-500 hover:text-stone-700",
                )}
              >
                {tab.label}
                <span
                  className={cn(
                    "flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-xs",
                    activeTab === tab.key
                      ? "bg-primary/10 text-primary-dark"
                      : "bg-stone-200 text-stone-500",
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
      )}

      {layout === "kanban" && (
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-stone-500">
            排期 {counts.queued} · 已发布 {counts.live}
          </p>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="搜索看板…"
              className="h-9 w-60 rounded-lg border border-stone-300 bg-white pl-9 pr-3 text-sm placeholder:text-stone-400 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
          </div>
        </div>
      )}

      {listError && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          {listError}
        </div>
      )}

      {layout === "kanban" ? (
        boardLoading || !board ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="h-96 animate-pulse rounded-xl border border-stone-200 bg-stone-100"
              />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            {(
              [
                ["pending", "待审核", board.pending],
                ["approved", "已通过", board.approved],
                ["queued", "已排期", board.queued],
                ["live", "已发布", board.live],
              ] as const
            ).map(([key, label, col]) => (
              <div
                key={key}
                className="flex max-h-[min(70vh,900px)] flex-col rounded-xl border border-stone-200 bg-stone-50/80"
              >
                <div className="border-b border-stone-200 px-3 py-2">
                  <h2 className="text-sm font-semibold text-stone-800">
                    {label}
                    <span className="ml-2 font-normal text-stone-500">
                      ({filterItems(col).length})
                    </span>
                  </h2>
                </div>
                <div className="flex flex-1 flex-col gap-3 overflow-y-auto p-3">
                  {filterItems(col).map((item) => (
                    <div key={item.id} className="space-y-2">
                      <button
                        type="button"
                        className="block w-full text-left"
                        onClick={() => setDetailId(item.id)}
                      >
                        <NotePackageCard
                          title={cardTitle(item)}
                          coverUrl={item.cover_url ?? undefined}
                          score={
                            item.ranking_score != null
                              ? Math.round(item.ranking_score)
                              : undefined
                          }
                          styleFamily={item.style_family ?? undefined}
                          complianceStatus={complianceToCardStatus(
                            item.compliance_status,
                          )}
                          onApprove={
                            key === "pending"
                              ? () => handleApprove(item.id)
                              : undefined
                          }
                          onReject={
                            key === "pending"
                              ? () => handleReject(item.id)
                              : undefined
                          }
                        />
                      </button>
                      {key === "approved" && (
                        <button
                          type="button"
                          onClick={() => patchStatus(item.id, "queued")}
                          className="w-full rounded-lg border border-stone-300 bg-white py-1.5 text-xs text-stone-700 hover:bg-stone-50"
                        >
                          移入已排期
                        </button>
                      )}
                      {key === "queued" && (
                        <button
                          type="button"
                          onClick={() => patchStatus(item.id, "live")}
                          className="w-full rounded-lg border border-emerald-200 bg-emerald-50 py-1.5 text-xs text-emerald-800 hover:bg-emerald-100/80"
                        >
                          标记已发布
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )
      ) : loading ? (
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
              <div key={item.id} className="space-y-2">
                <button
                  type="button"
                  className="block w-full text-left"
                  onClick={() => setDetailId(item.id)}
                >
                  <NotePackageCard
                    title={cardTitle(item)}
                    coverUrl={item.cover_url ?? undefined}
                    score={
                      item.ranking_score != null
                        ? Math.round(item.ranking_score)
                        : undefined
                    }
                    styleFamily={item.style_family ?? undefined}
                    complianceStatus={complianceToCardStatus(
                      item.compliance_status,
                    )}
                    onApprove={() => handleApprove(item.id)}
                    onReject={() => handleReject(item.id)}
                  />
                </button>
              </div>
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
            <button
              key={item.id}
              type="button"
              className="block w-full text-left"
              onClick={() => setDetailId(item.id)}
            >
              <NotePackageCard
                title={cardTitle(item)}
                coverUrl={item.cover_url ?? undefined}
                score={
                  item.ranking_score != null
                    ? Math.round(item.ranking_score)
                    : undefined
                }
                styleFamily={item.style_family ?? undefined}
                complianceStatus={complianceToCardStatus(
                  item.compliance_status,
                )}
              />
            </button>
          ))}
        </div>
      )}

      {detailId && (
        <div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center sm:p-6">
          <button
            type="button"
            className="absolute inset-0 bg-black/40"
            aria-label="关闭"
            onClick={() => {
              setDetailId(null);
              setEditTitleId(null);
            }}
          />
          <div className="relative max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-t-2xl border border-stone-200 bg-white p-5 shadow-xl sm:rounded-2xl">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-stone-900">文案变体</h3>
              <button
                type="button"
                onClick={() => {
                  setDetailId(null);
                  setEditTitleId(null);
                }}
                className="rounded p-1 text-stone-400 hover:bg-stone-100 hover:text-stone-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            {detailLoading ? (
              <p className="text-sm text-stone-500">加载中…</p>
            ) : detail ? (
              <div className="space-y-3">
                {detail.text_assets
                  .filter((t) => t.asset_role === "title")
                  .map((t) => (
                    <div
                      key={t.id}
                      className="rounded-lg border border-stone-100 bg-stone-50 p-3"
                    >
                      {editTitleId === t.id ? (
                        <div className="space-y-2">
                          <textarea
                            value={editTitleText}
                            onChange={(e) => setEditTitleText(e.target.value)}
                            rows={3}
                            className="w-full rounded border border-stone-300 p-2 text-sm"
                          />
                          <div className="flex gap-2">
                            <button
                              type="button"
                              onClick={() => void saveTitleAsset()}
                              className="rounded-lg bg-primary px-3 py-1.5 text-xs text-white"
                            >
                              保存
                            </button>
                            <button
                              type="button"
                              onClick={() => setEditTitleId(null)}
                              className="rounded-lg border border-stone-300 px-3 py-1.5 text-xs"
                            >
                              取消
                            </button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <p className="text-sm text-stone-800">{t.content}</p>
                          <button
                            type="button"
                            onClick={() => {
                              setEditTitleId(t.id);
                              setEditTitleText(t.content);
                            }}
                            className="mt-2 text-xs text-primary-dark hover:underline"
                          >
                            编辑标题
                          </button>
                        </>
                      )}
                    </div>
                  ))}
                {!detail.text_assets.some((t) => t.asset_role === "title") && (
                  <p className="text-sm text-stone-500">暂无可编辑标题</p>
                )}
              </div>
            ) : (
              <p className="text-sm text-stone-500">无法加载详情</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
