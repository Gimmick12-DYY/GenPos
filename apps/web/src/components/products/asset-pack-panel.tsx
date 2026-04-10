"use client";

import { useCallback, useEffect, useState } from "react";
import { Layers, Loader2, Pencil, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";

interface AssetPackRow {
  id: string;
  quarter_label: string;
  status: string;
  effective_from: string | null;
  effective_to: string | null;
  created_at: string;
  updated_at: string;
}

interface PackListResponse {
  items: AssetPackRow[];
  total: number;
}

const STATUS_ORDER: Record<string, number> = {
  active: 0,
  pending_review: 1,
  draft: 2,
  archived: 3,
};

function statusLabel(s: string): string {
  switch (s) {
    case "draft":
      return "草稿";
    case "pending_review":
      return "待审核";
    case "active":
      return "生效中";
    case "archived":
      return "已归档";
    default:
      return s;
  }
}

function statusBadgeClass(s: string): string {
  switch (s) {
    case "active":
      return "bg-emerald-100 text-emerald-800";
    case "pending_review":
      return "bg-amber-100 text-amber-900";
    case "draft":
      return "bg-stone-100 text-stone-700";
    case "archived":
      return "bg-stone-200/80 text-stone-600";
    default:
      return "bg-stone-100 text-stone-700";
  }
}

export function AssetPackPanel(props: {
  onContinueDraft: (packId: string) => void;
  onPacksChanged?: () => void;
}) {
  const { onContinueDraft, onPacksChanged } = props;
  const [items, setItems] = useState<AssetPackRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<PackListResponse>(
        "/asset-packs?limit=50&offset=0"
      );
      const rows = [...(res.items || [])];
      rows.sort((a, b) => {
        const da = STATUS_ORDER[a.status] ?? 99;
        const db = STATUS_ORDER[b.status] ?? 99;
        if (da !== db) return da - db;
        return b.created_at.localeCompare(a.created_at);
      });
      setItems(rows);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载素材包失败");
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function activatePack(id: string) {
    if (
      !window.confirm(
        "确认将该素材包设为「生效中」？同季度下其他生效包将被归档。"
      )
    ) {
      return;
    }
    setBusyId(id);
    setError(null);
    try {
      await api.post<AssetPackRow>(`/asset-packs/${id}/activate`);
      await load();
      onPacksChanged?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : "激活失败");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <Card className="mb-8">
      <CardContent className="p-5">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Layers className="h-5 w-5 text-stone-500" />
            <h2 className="text-base font-semibold text-stone-900">素材包时间线</h2>
          </div>
          <Button type="button" variant="outline" size="sm" onClick={() => void load()}>
            刷新
          </Button>
        </div>
        {error && (
          <p className="mb-3 text-sm text-red-700">{error}</p>
        )}
        {loading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : items.length === 0 ? (
          <p className="py-6 text-center text-sm text-stone-500">
            暂无素材包。点击「上传素材包」创建季度素材。
          </p>
        ) : (
          <ul className="divide-y divide-stone-100">
            {items.map((p) => (
              <li
                key={p.id}
                className="flex flex-wrap items-center gap-3 py-3 first:pt-0 last:pb-0"
              >
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusBadgeClass(p.status)}`}
                >
                  {statusLabel(p.status)}
                </span>
                <span className="font-medium text-stone-900">{p.quarter_label}</span>
                <span className="text-xs text-stone-400">
                  {p.effective_from || "—"} → {p.effective_to || "—"}
                </span>
                <div className="ml-auto flex flex-wrap items-center gap-2">
                  {p.status === "draft" && (
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => onContinueDraft(p.id)}
                    >
                      <Pencil className="h-3.5 w-3.5" />
                      继续编辑
                    </Button>
                  )}
                  {p.status === "pending_review" && (
                    <Button
                      type="button"
                      size="sm"
                      disabled={busyId === p.id}
                      onClick={() => void activatePack(p.id)}
                    >
                      {busyId === p.id ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Sparkles className="h-3.5 w-3.5" />
                      )}
                      激活上线
                    </Button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
