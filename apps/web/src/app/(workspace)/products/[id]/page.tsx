"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  FileText,
  Loader2,
  Package,
  ImageIcon,
} from "lucide-react";
import { PageHeader, PageShell } from "@/components/layout/page-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api } from "@/lib/api";
import { ensureAuth } from "@/lib/auth";

interface Product {
  id: string;
  merchant_id: string;
  name: string;
  category: string;
  status: string;
  primary_objective: string | null;
  description: string | null;
}

interface AssetRow {
  id: string;
  type: string;
  storage_url: string;
  width: number | null;
  height: number | null;
  approval_status: string;
}

interface AssetListResponse {
  items: AssetRow[];
  total: number;
  limit: number;
  offset: number;
}

interface NotePackageRow {
  id: string;
  review_status: string;
  objective: string;
  source_mode: string;
  created_at: string;
  cover_url: string | null;
}

interface NotePackageListResponse {
  items: NotePackageRow[];
  total: number;
}

export default function ProductDetailPage() {
  const params = useParams();
  const productId = typeof params.id === "string" ? params.id : "";

  const [product, setProduct] = useState<Product | null>(null);
  const [assets, setAssets] = useState<AssetRow[]>([]);
  const [assetTotal, setAssetTotal] = useState(0);
  const [noteRows, setNoteRows] = useState<NotePackageRow[]>([]);
  const [noteTotal, setNoteTotal] = useState(0);
  const [activePackOnly, setActivePackOnly] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!productId) return;
    setLoading(true);
    setError(null);
    try {
      const qs = new URLSearchParams({ limit: "48", offset: "0" });
      if (activePackOnly) qs.set("pack_status", "active");
      const [p, a, notes] = await Promise.all([
        api.get<Product>(`/products/${productId}`),
        api.get<AssetListResponse>(
          `/products/${productId}/assets?${qs.toString()}`
        ),
        api.get<NotePackageListResponse>(
          `/note-packages?product_id=${encodeURIComponent(productId)}&limit=20&offset=0&sort=recent`
        ),
      ]);
      setProduct(p);
      setAssets(a.items || []);
      setAssetTotal(a.total ?? 0);
      setNoteRows(notes.items || []);
      setNoteTotal(notes.total ?? 0);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
      setProduct(null);
      setAssets([]);
      setNoteRows([]);
    } finally {
      setLoading(false);
    }
  }, [productId, activePackOnly]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      await ensureAuth();
      if (cancelled) return;
      await load();
    })();
    return () => {
      cancelled = true;
    };
  }, [load]);

  return (
    <PageShell>
      <div className="mb-4">
        <Link
          href="/products"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-stone-600 hover:text-stone-900"
        >
          <ArrowLeft className="h-4 w-4" />
          返回产品库
        </Link>
      </div>

      {error && (
        <div className="mb-4 rounded-2xl border border-red-200/80 bg-red-50 px-4 py-3 text-sm text-red-900">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex min-h-[240px] items-center justify-center">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
        </div>
      ) : product ? (
        <>
          <PageHeader
            icon={Package}
            title={product.name}
            description={`${product.category} · 状态 ${product.status}`}
          />

          {product.description && (
            <p className="mb-6 max-w-2xl text-sm text-stone-600">{product.description}</p>
          )}

          <Card className="mb-8">
            <CardContent className="p-5">
              <div className="mb-3 flex items-center gap-2">
                <FileText className="h-5 w-5 text-stone-500" />
                <h2 className="text-base font-semibold text-stone-900">
                  最近笔记包
                  <span className="ml-2 text-sm font-normal text-stone-500">
                    （共 {noteTotal} 条）
                  </span>
                </h2>
              </div>
              {noteRows.length === 0 ? (
                <p className="text-sm text-stone-500">暂无关联笔记包。</p>
              ) : (
                <ul className="divide-y divide-stone-100">
                  {noteRows.map((n) => (
                    <li
                      key={n.id}
                      className="flex flex-wrap items-center gap-3 py-3 first:pt-0 last:pb-0"
                    >
                      <span className="rounded-full bg-stone-100 px-2 py-0.5 text-xs text-stone-700">
                        {n.review_status}
                      </span>
                      <span className="text-sm text-stone-800">{n.objective}</span>
                      <span className="text-xs text-stone-400">
                        {n.source_mode} ·{" "}
                        {n.created_at ? n.created_at.slice(0, 10) : "—"}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
              <p className="mt-3 text-xs text-stone-400">
                完整审核与发布流程见「内容工厂」与「今日推荐」。
              </p>
            </CardContent>
          </Card>

          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-base font-semibold text-stone-900">
              关联素材
              <span className="ml-2 text-sm font-normal text-stone-500">
                （{assetTotal} 张）
              </span>
            </h2>
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant={activePackOnly ? "primary" : "outline"}
                size="sm"
                onClick={() => setActivePackOnly(true)}
              >
                仅生效素材包
              </Button>
              <Button
                type="button"
                variant={!activePackOnly ? "primary" : "outline"}
                size="sm"
                onClick={() => setActivePackOnly(false)}
              >
                全部素材包
              </Button>
            </div>
          </div>

          {assets.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-14 text-center">
                <ImageIcon className="h-10 w-10 text-stone-300" />
                <p className="mt-3 text-sm text-stone-500">
                  {activePackOnly
                    ? "当前生效包中暂无关联到该产品的素材。可切换到「全部素材包」查看草稿/历史包中的素材。"
                    : "暂无关联素材。在「上传素材包」中为素材选择本产品即可关联。"}
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
              {assets.map((a) => (
                <Card key={a.id} className="overflow-hidden">
                  <div className="relative aspect-square bg-stone-100">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={a.storage_url}
                      alt=""
                      className="h-full w-full object-cover"
                    />
                    <span className="absolute left-2 top-2 rounded bg-stone-900/75 px-1.5 py-0.5 text-[10px] font-medium text-white">
                      {a.type}
                    </span>
                    <span
                      className={`absolute right-2 top-2 rounded px-1.5 py-0.5 text-[10px] font-medium ${
                        a.approval_status === "approved"
                          ? "bg-emerald-600 text-white"
                          : a.approval_status === "rejected"
                            ? "bg-red-600 text-white"
                            : "bg-amber-500 text-white"
                      }`}
                    >
                      {a.approval_status}
                    </span>
                  </div>
                  <CardContent className="p-2">
                    <p className="truncate text-xs text-stone-500">
                      {a.width && a.height ? `${a.width}×${a.height}` : "—"}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </>
      ) : null}
    </PageShell>
  );
}
