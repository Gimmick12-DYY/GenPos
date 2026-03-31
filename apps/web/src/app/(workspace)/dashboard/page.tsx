"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { NotePackageCard } from "@/components/note-package-card";
import { Sparkles, TrendingUp, Eye, CalendarDays, Play } from "lucide-react";
import { api } from "@/lib/api";
import { ensureAuth, getMerchantId } from "@/lib/auth";

interface NotePackageItem {
  id: string;
  product_id: string;
  objective: string;
  ranking_score?: number | null;
  style_family?: string | null;
  compliance_status: string;
  review_status: string;
  cover_url?: string | null;
  product_name?: string | null;
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

function cardTitle(pkg: NotePackageItem): string {
  if (pkg.product_name) {
    return pkg.style_family
      ? `${pkg.product_name} · ${pkg.style_family}`
      : pkg.product_name;
  }
  return pkg.style_family ? `笔记 · ${pkg.style_family}` : "笔记方案";
}

function todayIsoDate(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export default function DashboardPage() {
  const [queue, setQueue] = useState<ReviewQueueResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [pickDate, setPickDate] = useState(todayIsoDate);
  const [runningBatch, setRunningBatch] = useState(false);
  const [generatingProductId, setGeneratingProductId] = useState<string | null>(
    null
  );
  const [infoMessage, setInfoMessage] = useState<string | null>(null);

  useEffect(() => {
    ensureAuth()
      .then(() => setAuthReady(true))
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  const loadQueue = useCallback(async () => {
    if (!authReady) return;
    const merchantId = getMerchantId();
    if (!merchantId) return;

    setLoading(true);
    setError(null);
    try {
      const res = await api.get<ReviewQueueResponse>(
        `/review/queue/today?merchant_id=${merchantId}&limit=50&offset=0&for_date=${pickDate}`
      );
      setQueue(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
      setQueue(null);
    } finally {
      setLoading(false);
    }
  }, [authReady, pickDate]);

  useEffect(() => {
    void loadQueue();
  }, [loadQueue]);

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

  async function runDailyBatch() {
    const merchantId = getMerchantId();
    if (!merchantId) return;
    setRunningBatch(true);
    setError(null);
    setInfoMessage(null);
    try {
      await api.post("/generate/daily/run", {
        merchant_id: merchantId,
      });
      await loadQueue();
    } catch (e) {
      setError(e instanceof Error ? e.message : "批次触发失败");
    } finally {
      setRunningBatch(false);
    }
  }

  async function handleGenerateMore(pkg: NotePackageItem) {
    const merchantId = getMerchantId();
    if (!merchantId) return;
    setGeneratingProductId(pkg.product_id);
    setError(null);
    setInfoMessage(null);
    try {
      const res = await api.post<Record<string, unknown>>("/generate/request", {
        merchant_id: merchantId,
        product_id: pkg.product_id,
        objective: pkg.objective || "种草",
        persona: undefined,
        style_preference: pkg.style_family ?? undefined,
      });
      if (
        res &&
        typeof res === "object" &&
        "mode" in res &&
        res.mode === "async"
      ) {
        setInfoMessage(
          "已提交一键生成任务（异步）。请稍后在「待审核」查看新笔记；今日推荐仅展示每日自动批次。"
        );
        return;
      }
      const sync = res as {
        note_package_id?: string;
        error?: string;
      };
      if (sync.error) {
        setError(sync.error);
        return;
      }
      if (sync.note_package_id) {
        setInfoMessage(
          "已生成新笔记包。请在「待审核」查看（一键生成不会自动进入今日推荐队列）。"
        );
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "触发生成失败");
    } finally {
      setGeneratingProductId(null);
    }
  }

  const items = queue?.items ?? [];
  const total = queue?.total ?? 0;
  const avgScore =
    items.length > 0
      ? (
          items.reduce((a, p) => a + (p.ranking_score ?? 0), 0) / items.length
        ).toFixed(1)
      : "—";

  if (error && !queue && !loading) {
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
        <div className="mb-2 flex flex-wrap items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-light shadow-sm">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl font-bold text-stone-900">今日推荐</h1>
            <p className="text-sm text-stone-500">
              当日自动批次生成的笔记（按 Asia/Shanghai
              日历日）；与「一键生成」内容区分开
            </p>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-stone-600">
            <CalendarDays className="h-4 w-4 text-stone-400" />
            <span>日期</span>
            <input
              type="date"
              value={pickDate}
              onChange={(e) => setPickDate(e.target.value)}
              className="rounded-lg border border-stone-300 bg-white px-2 py-1 text-sm"
            />
          </label>
          <button
            type="button"
            onClick={() => void runDailyBatch()}
            disabled={runningBatch || !authReady}
            className="inline-flex items-center gap-1.5 rounded-lg border border-primary/30 bg-primary/10 px-3 py-1.5 text-sm font-medium text-primary-dark hover:bg-primary/15 disabled:opacity-50"
          >
            <Play className="h-3.5 w-3.5" />
            {runningBatch ? "运行中…" : "运行每日生成"}
          </button>
        </div>
      </div>

      {error && queue && (
        <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-900">
          {error}
        </div>
      )}
      {infoMessage && (
        <div className="mb-4 rounded-lg border border-primary/20 bg-primary/5 px-4 py-2 text-sm text-primary-dark">
          {infoMessage}
        </div>
      )}

      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="flex items-center gap-4 rounded-xl border border-stone-200 bg-surface-raised p-5">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <p className="text-2xl font-bold text-stone-900">
              {loading ? "…" : total}
            </p>
            <p className="text-sm text-stone-500">今日待审（自动批次）</p>
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
        <Link
          href="/review"
          className="text-sm font-medium text-primary transition-colors hover:text-primary-dark"
        >
          查看全部 →
        </Link>
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
          <p>该日暂无自动批次待审笔记</p>
          <p className="mx-auto mt-2 max-w-md text-sm">
            「今日推荐」只展示来源为每日自动任务（daily_auto）的包。请点击「运行每日生成」，或配置
            Temporal / <code className="text-xs">POST /generate/daily/run</code>
            。一键生成与对话产生的内容请在「待审核」查看。
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((pkg) => (
            <NotePackageCard
              key={pkg.id}
              title={cardTitle(pkg)}
              coverUrl={pkg.cover_url ?? undefined}
              score={
                pkg.ranking_score != null
                  ? Math.round(pkg.ranking_score * 100) / 100
                  : undefined
              }
              styleFamily={pkg.style_family ?? undefined}
              complianceStatus={complianceToCardStatus(pkg.compliance_status)}
              likes={0}
              comments={0}
              onApprove={() => handleApprove(pkg.id)}
              onReject={() => handleReject(pkg.id)}
              onGenerateMore={() => void handleGenerateMore(pkg)}
              generateMorePending={generatingProductId === pkg.product_id}
            />
          ))}
        </div>
      )}
    </div>
  );
}
