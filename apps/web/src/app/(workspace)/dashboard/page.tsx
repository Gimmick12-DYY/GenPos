"use client";

import { useEffect, useState } from "react";
import { NotePackageCard } from "@/components/note-package-card";
import { Sparkles, TrendingUp, Eye } from "lucide-react";
import { api } from "@/lib/api";
import { ensureAuth, getMerchantId } from "@/lib/auth";

interface NotePackageItem {
  id: string;
  ranking_score?: number | null;
  style_family?: string | null;
  compliance_status: string;
  review_status: string;
}

interface ReviewQueueResponse {
  items: NotePackageItem[];
  total: number;
  limit: number;
  offset: number;
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

export default function DashboardPage() {
  const [queue, setQueue] = useState<ReviewQueueResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    ensureAuth()
      .then(() => setAuthReady(true))
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!authReady) return;
    const merchantId = getMerchantId();
    if (!merchantId) return;

    setLoading(true);
    setError(null);
    api
      .get<ReviewQueueResponse>(
        `/review/queue/today?merchant_id=${merchantId}&limit=50&offset=0`
      )
      .then(setQueue)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [authReady]);

  async function handleApprove(id: string) {
    try {
      await api.post(`/review/${id}/approve`, {});
      setQueue((prev) =>
        prev
          ? {
              ...prev,
              items: prev.items.filter((p) => p.id !== id),
              total: Math.max(0, prev.total - 1),
            }
          : null
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "操作失败");
    }
  }

  async function handleReject(id: string) {
    const reason = window.prompt("拒绝原因（选填）：") ?? "未填写";
    try {
      await api.post(`/review/${id}/reject`, { reason: reason || "未填写" });
      setQueue((prev) =>
        prev
          ? {
              ...prev,
              items: prev.items.filter((p) => p.id !== id),
              total: Math.max(0, prev.total - 1),
            }
          : null
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "操作失败");
    }
  }

  const items = queue?.items ?? [];
  const total = queue?.total ?? 0;
  const avgScore =
    items.length > 0
      ? (
          items.reduce(
            (a, p) => a + (p.ranking_score ?? 0),
            0
          ) / items.length
        ).toFixed(1)
      : "—";

  if (error && !queue) {
    return (
      <div className="mx-auto max-w-7xl p-6 lg:p-8">
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center text-sm text-red-800">
          <p className="font-medium">加载失败</p>
          <p className="mt-1">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl p-6 lg:p-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-light shadow-sm">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-stone-900">今日推荐</h1>
            <p className="text-sm text-stone-500">
              基于品牌规则和市场趋势，为您精选的笔记内容方案
            </p>
          </div>
        </div>
      </div>

      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="flex items-center gap-4 rounded-xl border border-stone-200 bg-surface-raised p-5">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <p className="text-2xl font-bold text-stone-900">
              {loading ? "…" : total}
            </p>
            <p className="text-sm text-stone-500">待审核</p>
          </div>
        </div>
        <div className="flex items-center gap-4 rounded-xl border border-stone-200 bg-surface-raised p-5">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10">
            <TrendingUp className="h-6 w-6 text-accent" />
          </div>
          <div>
            <p className="text-2xl font-bold text-stone-900">{avgScore}</p>
            <p className="text-sm text-stone-500">平均评分</p>
          </div>
        </div>
        <div className="flex items-center gap-4 rounded-xl border border-stone-200 bg-surface-raised p-5">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50">
            <Eye className="h-6 w-6 text-blue-500" />
          </div>
          <div>
            <p className="text-2xl font-bold text-stone-900">—</p>
            <p className="text-sm text-stone-500">预估曝光</p>
          </div>
        </div>
      </div>

      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-stone-900">推荐笔记方案</h2>
        <a
          href="/review"
          className="text-sm font-medium text-primary hover:text-primary-dark transition-colors"
        >
          查看全部 →
        </a>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-80 animate-pulse rounded-xl border border-stone-200 bg-stone-100"
            />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="rounded-xl border border-stone-200 bg-surface-raised py-16 text-center text-stone-500">
          <p>暂无待审核的笔记方案</p>
          <p className="mt-1 text-sm">在「AI对话」或「一键生成」中生成内容后，会出现在这里</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((pkg) => (
            <NotePackageCard
              key={pkg.id}
              title={pkg.style_family ? `笔记 · ${pkg.style_family}` : "笔记方案"}
              score={pkg.ranking_score != null ? Math.round(pkg.ranking_score) : undefined}
              styleFamily={pkg.style_family ?? undefined}
              complianceStatus={complianceToCardStatus(pkg.compliance_status)}
              likes={0}
              comments={0}
              onApprove={() => handleApprove(pkg.id)}
              onReject={() => handleReject(pkg.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
