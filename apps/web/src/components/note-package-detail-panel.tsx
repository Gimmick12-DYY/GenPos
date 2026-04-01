"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { X } from "lucide-react";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/ui/badge";

interface TextAssetRow {
  id: string;
  asset_role: string;
  content: string;
}

interface ImageAssetRow {
  id: string;
  asset_role: string;
  image_url: string;
}

export interface NotePackageDetailModel {
  id: string;
  objective: string;
  style_family?: string | null;
  ranking_score?: number | null;
  compliance_status: string;
  review_status: string;
  cover_url?: string | null;
  product_name?: string | null;
  text_assets: TextAssetRow[];
  image_assets: ImageAssetRow[];
}

function roleLabel(role: string): string {
  const map: Record<string, string> = {
    title: "标题",
    body: "正文",
    first_comment: "首评",
    hashtag: "话题",
    cta: "行动号召",
    cover_text: "封面文案",
  };
  return map[role] ?? role;
}

interface NotePackageDetailPanelProps {
  packageId: string | null;
  onClose: () => void;
}

export function NotePackageDetailPanel({
  packageId,
  onClose,
}: NotePackageDetailPanelProps) {
  const [detail, setDetail] = useState<NotePackageDetailModel | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    if (!packageId) {
      setDetail(null);
      setErr(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setErr(null);
    void api
      .get<NotePackageDetailModel>(`/note-packages/${packageId}`)
      .then((d) => {
        if (!cancelled) setDetail(d);
      })
      .catch((e) => {
        if (!cancelled)
          setErr(e instanceof Error ? e.message : "加载失败");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [packageId]);

  if (!packageId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center sm:p-6">
      <button
        type="button"
        className="absolute inset-0 bg-stone-950/50 backdrop-blur-[2px]"
        aria-label="关闭"
        onClick={onClose}
      />
      <div className="relative max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-t-2xl border border-stone-200/80 bg-white p-5 shadow-2xl shadow-stone-900/15 sm:max-h-[85vh] sm:rounded-2xl">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold text-stone-900">笔记方案预览</h3>
            {detail?.product_name && (
              <p className="mt-0.5 text-sm text-stone-500">{detail.product_name}</p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 rounded-lg p-1 text-stone-400 hover:bg-stone-100 hover:text-stone-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {loading ? (
          <div className="space-y-3 py-4">
            <div className="h-40 animate-pulse rounded-xl bg-stone-100" />
            <div className="h-24 animate-pulse rounded-lg bg-stone-100" />
            <div className="h-24 animate-pulse rounded-lg bg-stone-100" />
          </div>
        ) : err ? (
          <p className="py-4 text-sm text-red-600">{err}</p>
        ) : detail ? (
          <div className="space-y-5">
            <div className="flex flex-wrap items-center gap-2">
              {detail.ranking_score != null && (
                <span className="rounded-full bg-stone-900 px-2.5 py-0.5 text-xs font-semibold text-white">
                  评分 {Math.round(detail.ranking_score * 100) / 100}
                </span>
              )}
              <StatusBadge
                status={
                  detail.compliance_status === "passed"
                    ? "passed"
                    : detail.compliance_status === "failed"
                      ? "failed"
                      : detail.compliance_status === "review_needed"
                        ? "review_needed"
                        : "pending"
                }
              />
              <span className="text-xs text-stone-500">
                {detail.objective}
                {detail.style_family ? ` · ${detail.style_family}` : ""}
              </span>
            </div>

            {detail.cover_url && (
              <div className="overflow-hidden rounded-xl border border-stone-100 bg-stone-50">
                <img
                  src={detail.cover_url}
                  alt=""
                  className="aspect-[3/4] w-full object-cover"
                  referrerPolicy="no-referrer"
                />
              </div>
            )}

            <div className="space-y-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-stone-400">
                文案与话题
              </p>
              {detail.text_assets.length === 0 ? (
                <p className="text-sm text-stone-500">暂无文本资产</p>
              ) : (
                detail.text_assets.map((t) => (
                  <div
                    key={t.id}
                    className="rounded-lg border border-stone-100 bg-stone-50/80 p-3"
                  >
                    <p className="mb-1 text-[11px] font-medium uppercase text-stone-400">
                      {roleLabel(t.asset_role)}
                    </p>
                    <p className="whitespace-pre-wrap text-sm leading-relaxed text-stone-800">
                      {t.content}
                    </p>
                  </div>
                ))
              )}
            </div>

            {detail.image_assets.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-stone-400">
                  图片素材
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {detail.image_assets.map((im) => (
                    <div
                      key={im.id}
                      className="overflow-hidden rounded-lg border border-stone-100 bg-stone-50"
                    >
                      {im.image_url ? (
                        <img
                          src={im.image_url}
                          alt={im.asset_role}
                          className="aspect-square w-full object-cover"
                          referrerPolicy="no-referrer"
                        />
                      ) : (
                        <div className="flex aspect-square items-center justify-center text-xs text-stone-400">
                          无图
                        </div>
                      )}
                      <p className="truncate px-1.5 py-1 text-[10px] text-stone-500">
                        {im.asset_role}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="border-t border-stone-100 pt-4">
              <Link
                href="/review"
                className="text-sm font-semibold text-primary hover:text-primary-dark"
                onClick={onClose}
              >
                在「待审核」中打开完整流程 →
              </Link>
            </div>
          </div>
        ) : (
          <p className="py-4 text-sm text-stone-500">无法加载详情</p>
        )}
      </div>
    </div>
  );
}
