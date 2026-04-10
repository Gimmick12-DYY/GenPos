"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  Check,
  ChevronLeft,
  ChevronRight,
  ImagePlus,
  Loader2,
  Upload,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

type AssetType =
  | "packshot"
  | "cutout"
  | "logo"
  | "packaging_ref"
  | "hero"
  | "other";

interface AssetPack {
  id: string;
  merchant_id: string;
  quarter_label: string;
  status: string;
  effective_from: string | null;
  effective_to: string | null;
  metadata_json?: Record<string, unknown> | null;
}

interface PackListResponse {
  items: AssetPack[];
  total: number;
}

interface AssetRow {
  id: string;
  asset_pack_id: string;
  product_id: string | null;
  type: AssetType;
  storage_url: string;
  width: number | null;
  height: number | null;
  approval_status: "pending" | "approved" | "rejected";
  created_at: string;
}

interface AssetListResponse {
  items: AssetRow[];
  total: number;
}

interface ProductOption {
  id: string;
  name: string;
}

const ASSET_TYPES: { value: AssetType; label: string }[] = [
  { value: "packshot", label: "产品主图 (packshot)" },
  { value: "cutout", label: "抠图 (cutout)" },
  { value: "logo", label: "Logo" },
  { value: "packaging_ref", label: "包装参考" },
  { value: "hero", label: "主视觉 (hero)" },
  { value: "other", label: "其他" },
];

const MAX_BATCH = 50;

function pickImageFiles(list: Iterable<File>): File[] {
  return Array.from(list).filter((f) => f.type.startsWith("image/"));
}

export function AssetPackWizard(props: {
  open: boolean;
  onClose: () => void;
  products: ProductOption[];
  onSubmitted?: () => void;
  /** Open wizard directly on this pack (draft resume from parent). */
  bootPackId?: string | null;
  onBootPackHandled?: () => void;
}) {
  const { open, onClose, products, onSubmitted, bootPackId, onBootPackHandled } =
    props;
  const onBootHandledRef = useRef(onBootPackHandled);
  onBootHandledRef.current = onBootPackHandled;
  const [step, setStep] = useState(1);
  const [packId, setPackId] = useState<string | null>(null);
  const [quarterLabel, setQuarterLabel] = useState("2026_Q2");
  const [effectiveFrom, setEffectiveFrom] = useState("");
  const [effectiveTo, setEffectiveTo] = useState("");
  const [draftPacks, setDraftPacks] = useState<AssetPack[]>([]);
  const [loadingDrafts, setLoadingDrafts] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadQueue, setUploadQueue] = useState<File[]>([]);
  const [uploadDone, setUploadDone] = useState(0);
  const [assets, setAssets] = useState<AssetRow[]>([]);
  const [localTags, setLocalTags] = useState<
    Record<string, { type: AssetType; product_id: string }>
  >({});
  const [bootLoading, setBootLoading] = useState(false);
  const [dropActive, setDropActive] = useState(false);

  const reset = useCallback(() => {
    setStep(1);
    setPackId(null);
    setQuarterLabel("2026_Q2");
    setEffectiveFrom("");
    setEffectiveTo("");
    setError(null);
    setUploadQueue([]);
    setUploadDone(0);
    setAssets([]);
    setLocalTags({});
    setBootLoading(false);
    setDropActive(false);
  }, []);

  useEffect(() => {
    if (!open || !bootPackId?.trim()) return;
    let cancelled = false;
    setBootLoading(true);
    setError(null);
    (async () => {
      try {
        const pack = await api.get<AssetPack>(`/asset-packs/${bootPackId.trim()}`);
        if (cancelled) return;
        setPackId(pack.id);
        setQuarterLabel(pack.quarter_label);
        setEffectiveFrom(
          pack.effective_from ? pack.effective_from.slice(0, 10) : ""
        );
        setEffectiveTo(pack.effective_to ? pack.effective_to.slice(0, 10) : "");
        const res = await api.get<AssetListResponse>(
          `/asset-packs/${pack.id}/assets?limit=100&offset=0`
        );
        const rows = res.items || [];
        setAssets(rows);
        const next: Record<string, { type: AssetType; product_id: string }> = {};
        for (const a of rows) {
          next[a.id] = {
            type: a.type,
            product_id: a.product_id || "",
          };
        }
        setLocalTags(next);
        setStep(rows.length > 0 ? 3 : 2);
        onBootHandledRef.current?.();
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "无法打开素材包");
          onBootHandledRef.current?.();
        }
      } finally {
        if (!cancelled) setBootLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [open, bootPackId]);

  useEffect(() => {
    if (!open) {
      reset();
      return;
    }
    let cancelled = false;
    (async () => {
      setLoadingDrafts(true);
      try {
        const res = await api.get<PackListResponse>(
          "/asset-packs?status=draft&limit=30&offset=0"
        );
        if (!cancelled) setDraftPacks(res.items || []);
      } catch {
        if (!cancelled) setDraftPacks([]);
      } finally {
        if (!cancelled) setLoadingDrafts(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [open, reset]);

  async function loadAssets(pid: string) {
    const res = await api.get<AssetListResponse>(
      `/asset-packs/${pid}/assets?limit=100&offset=0`
    );
    const rows = res.items || [];
    setAssets(rows);
    const next: Record<string, { type: AssetType; product_id: string }> = {};
    for (const a of rows) {
      next[a.id] = {
        type: a.type,
        product_id: a.product_id || "",
      };
    }
    setLocalTags(next);
  }

  async function createPackAndContinue() {
    if (!quarterLabel.trim()) {
      setError("请填写季度标签，例如 2026_Q2");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const body: Record<string, unknown> = {
        quarter_label: quarterLabel.trim(),
      };
      if (effectiveFrom.trim()) body.effective_from = effectiveFrom.trim();
      if (effectiveTo.trim()) body.effective_to = effectiveTo.trim();
      const pack = await api.post<AssetPack>("/asset-packs", body);
      setPackId(pack.id);
      setStep(2);
    } catch (e) {
      setError(e instanceof Error ? e.message : "创建失败");
    } finally {
      setBusy(false);
    }
  }

  async function resumeDraft(p: AssetPack) {
    setPackId(p.id);
    setQuarterLabel(p.quarter_label);
    setEffectiveFrom(p.effective_from || "");
    setEffectiveTo(p.effective_to || "");
    setBusy(true);
    setError(null);
    try {
      const res = await api.get<AssetListResponse>(
        `/asset-packs/${p.id}/assets?limit=100&offset=0`
      );
      const rows = res.items || [];
      setAssets(rows);
      const next: Record<string, { type: AssetType; product_id: string }> = {};
      for (const a of rows) {
        next[a.id] = {
          type: a.type,
          product_id: a.product_id || "",
        };
      }
      setLocalTags(next);
      setStep(rows.length > 0 ? 3 : 2);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    } finally {
      setBusy(false);
    }
  }

  async function runUploads() {
    if (!packId || uploadQueue.length === 0) return;
    setBusy(true);
    setError(null);
    setUploadDone(0);
    const files = uploadQueue.slice(0, MAX_BATCH);
    try {
      for (let i = 0; i < files.length; i++) {
        const fd = new FormData();
        fd.append("file", files[i]);
        fd.append("asset_type", "packshot");
        await api.postForm<AssetRow>(`/asset-packs/${packId}/assets`, fd);
        setUploadDone(i + 1);
      }
      setUploadQueue([]);
      await loadAssets(packId);
      setStep(3);
    } catch (e) {
      setError(e instanceof Error ? e.message : "上传失败");
    } finally {
      setBusy(false);
    }
  }

  async function saveTags(assetId: string) {
    if (!packId) return;
    const t = localTags[assetId];
    if (!t) return;
    setBusy(true);
    setError(null);
    try {
      const body: { type?: AssetType; product_id?: string | null } = {
        type: t.type,
      };
      body.product_id = t.product_id ? t.product_id : null;
      const updated = await api.patch<AssetRow>(
        `/asset-packs/${packId}/assets/${assetId}`,
        body
      );
      setAssets((prev) => prev.map((a) => (a.id === assetId ? updated : a)));
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存失败");
    } finally {
      setBusy(false);
    }
  }

  async function approveAsset(assetId: string) {
    if (!packId) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await api.post<AssetRow>(
        `/asset-packs/${packId}/assets/${assetId}/approve`
      );
      setAssets((prev) => prev.map((a) => (a.id === assetId ? updated : a)));
    } catch (e) {
      setError(e instanceof Error ? e.message : "操作失败");
    } finally {
      setBusy(false);
    }
  }

  async function submitPack() {
    if (!packId) return;
    setBusy(true);
    setError(null);
    try {
      await api.post(`/asset-packs/${packId}/submit`);
      onSubmitted?.();
      onClose();
      reset();
    } catch (e) {
      setError(e instanceof Error ? e.message : "提交失败");
    } finally {
      setBusy(false);
    }
  }

  const approvedPackshots = assets.filter(
    (a) => a.type === "packshot" && a.approval_status === "approved"
  ).length;

  if (!open) return null;

  const showBootSpinner = Boolean(bootPackId?.trim() && bootLoading);

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-stone-950/70 p-4 backdrop-blur-sm">
      <div className="flex max-h-[90vh] w-full max-w-2xl flex-col rounded-2xl border border-stone-200/80 bg-white shadow-2xl shadow-stone-900/20">
        <div className="flex shrink-0 items-center justify-between border-b border-stone-200 px-5 py-4">
          <div>
            <h2 className="text-lg font-semibold text-stone-900">上传素材包</h2>
            <p className="text-xs text-stone-500">
              步骤 {step}/4 · 草稿 → 待审核（需至少 1 张已通过的 packshot）
            </p>
          </div>
          <button
            type="button"
            onClick={() => {
              onClose();
              reset();
            }}
            className="rounded p-1 text-stone-400 hover:bg-stone-100 hover:text-stone-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
          {error && (
            <div className="mb-4 rounded-xl border border-red-200/80 bg-red-50 px-3 py-2 text-sm text-red-900">
              {error}
            </div>
          )}

          {showBootSpinner && (
            <div className="flex min-h-[200px] flex-col items-center justify-center gap-3 text-stone-500">
              <Loader2 className="h-10 w-10 animate-spin text-primary" />
              <p className="text-sm">正在打开素材包…</p>
            </div>
          )}

          {!showBootSpinner && step === 1 && (
            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-stone-700">
                  季度标签
                </label>
                <input
                  value={quarterLabel}
                  onChange={(e) => setQuarterLabel(e.target.value)}
                  className="input-surface h-10 w-full rounded-xl px-3 text-sm"
                  placeholder="2026_Q2"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="block text-sm font-medium text-stone-700">
                    生效开始（选填）
                  </label>
                  <input
                    type="date"
                    value={effectiveFrom}
                    onChange={(e) => setEffectiveFrom(e.target.value)}
                    className="input-surface h-10 w-full rounded-xl px-3 text-sm"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="block text-sm font-medium text-stone-700">
                    生效结束（选填）
                  </label>
                  <input
                    type="date"
                    value={effectiveTo}
                    onChange={(e) => setEffectiveTo(e.target.value)}
                    className="input-surface h-10 w-full rounded-xl px-3 text-sm"
                  />
                </div>
              </div>

              <Button
                type="button"
                onClick={createPackAndContinue}
                disabled={busy}
                className="w-full sm:w-auto"
              >
                {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                创建草稿并继续
              </Button>

              <div className="border-t border-stone-100 pt-4">
                <p className="mb-2 text-sm font-medium text-stone-700">
                  继续编辑草稿
                </p>
                {loadingDrafts ? (
                  <Loader2 className="h-6 w-6 animate-spin text-stone-400" />
                ) : draftPacks.length === 0 ? (
                  <p className="text-sm text-stone-500">暂无草稿</p>
                ) : (
                  <ul className="max-h-40 space-y-2 overflow-y-auto">
                    {draftPacks.map((p) => (
                      <li key={p.id}>
                        <button
                          type="button"
                          onClick={() => resumeDraft(p)}
                          disabled={busy}
                          className="flex w-full items-center justify-between rounded-xl border border-stone-200 px-3 py-2 text-left text-sm hover:bg-stone-50"
                        >
                          <span className="font-medium text-stone-800">
                            {p.quarter_label}
                          </span>
                          <span className="text-xs text-stone-500">{p.id.slice(0, 8)}…</span>
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}

          {!showBootSpinner && step === 2 && packId && (
            <div className="space-y-4">
              <p className="text-sm text-stone-600">
                单次最多 {MAX_BATCH} 张。默认类型为 packshot，可在下一步调整。支持拖拽到下方区域。
              </p>
              <label
                className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed py-10 transition-colors hover:border-primary/40 hover:bg-stone-50 ${
                  dropActive
                    ? "border-primary bg-primary/5"
                    : "border-stone-200 bg-stone-50/80"
                }`}
                onDragOver={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setDropActive(true);
                }}
                onDragLeave={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setDropActive(false);
                }}
                onDrop={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setDropActive(false);
                  const files = pickImageFiles(e.dataTransfer.files);
                  setUploadQueue(files.slice(0, MAX_BATCH));
                }}
              >
                <ImagePlus className="h-10 w-10 text-stone-400" />
                <span className="mt-2 text-sm text-stone-600">
                  点击选择或拖拽图片到此处
                </span>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  className="hidden"
                  onChange={(e) => {
                    const list = e.target.files
                      ? pickImageFiles(e.target.files)
                      : [];
                    setUploadQueue(list.slice(0, MAX_BATCH));
                  }}
                />
              </label>
              {uploadQueue.length > 0 && (
                <p className="text-sm text-stone-600">
                  已选 {uploadQueue.length} 个文件
                  {busy && uploadDone > 0
                    ? ` · 已上传 ${uploadDone}/${Math.min(uploadQueue.length, MAX_BATCH)}`
                    : null}
                </p>
              )}
              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setStep(1)}
                  disabled={busy}
                >
                  <ChevronLeft className="h-4 w-4" />
                  上一步
                </Button>
                <Button
                  type="button"
                  onClick={runUploads}
                  disabled={busy || uploadQueue.length === 0}
                >
                  {busy ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Upload className="h-4 w-4" />
                  )}
                  开始上传
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={async () => {
                    if (!packId) return;
                    setBusy(true);
                    setError(null);
                    try {
                      await loadAssets(packId);
                      setStep(3);
                    } catch (e) {
                      setError(e instanceof Error ? e.message : "加载失败");
                    } finally {
                      setBusy(false);
                    }
                  }}
                  disabled={busy}
                >
                  跳过（已有素材）
                </Button>
              </div>
            </div>
          )}

          {!showBootSpinner && step === 3 && packId && (
            <div className="space-y-4">
              <p className="text-sm text-stone-600">
                为每张图选择类型与关联产品，保存后点击「通过」标记审核。提交前至少需要 1 张已通过的
                packshot。
              </p>
              {assets.length === 0 ? (
                <p className="text-sm text-stone-500">暂无素材，请返回上一步上传。</p>
              ) : (
                <ul className="space-y-4">
                  {assets.map((a) => {
                    const tag = localTags[a.id] || {
                      type: a.type,
                      product_id: a.product_id || "",
                    };
                    return (
                      <li
                        key={a.id}
                        className="flex gap-3 rounded-xl border border-stone-200 p-3"
                      >
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={a.storage_url}
                          alt=""
                          className="h-20 w-20 shrink-0 rounded-lg object-cover"
                        />
                        <div className="min-w-0 flex-1 space-y-2">
                          <div className="flex flex-wrap items-center gap-2">
                            <span
                              className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                                a.approval_status === "approved"
                                  ? "bg-emerald-100 text-emerald-800"
                                  : a.approval_status === "rejected"
                                    ? "bg-red-100 text-red-800"
                                    : "bg-amber-100 text-amber-800"
                              }`}
                            >
                              {a.approval_status === "approved"
                                ? "已通过"
                                : a.approval_status === "rejected"
                                  ? "已拒绝"
                                  : "待审核"}
                            </span>
                            {a.width && a.height ? (
                              <span className="text-xs text-stone-400">
                                {a.width}×{a.height}
                              </span>
                            ) : null}
                          </div>
                          <select
                            className="input-surface h-9 w-full max-w-xs rounded-lg px-2 text-sm"
                            value={tag.type}
                            onChange={(e) =>
                              setLocalTags((prev) => ({
                                ...prev,
                                [a.id]: {
                                  ...tag,
                                  type: e.target.value as AssetType,
                                },
                              }))
                            }
                          >
                            {ASSET_TYPES.map((o) => (
                              <option key={o.value} value={o.value}>
                                {o.label}
                              </option>
                            ))}
                          </select>
                          <select
                            className="input-surface h-9 w-full max-w-xs rounded-lg px-2 text-sm"
                            value={tag.product_id}
                            onChange={(e) =>
                              setLocalTags((prev) => ({
                                ...prev,
                                [a.id]: {
                                  ...tag,
                                  product_id: e.target.value,
                                },
                              }))
                            }
                          >
                            <option value="">不关联产品</option>
                            {products.map((p) => (
                              <option key={p.id} value={p.id}>
                                {p.name}
                              </option>
                            ))}
                          </select>
                          <div className="flex flex-wrap gap-2">
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => saveTags(a.id)}
                              disabled={busy}
                            >
                              保存标签
                            </Button>
                            <Button
                              type="button"
                              size="sm"
                              onClick={() => approveAsset(a.id)}
                              disabled={busy || a.approval_status !== "pending"}
                            >
                              <Check className="h-3.5 w-3.5" />
                              通过
                            </Button>
                          </div>
                        </div>
                      </li>
                    );
                  })}
                </ul>
              )}
              <div className="flex flex-wrap gap-2 border-t border-stone-100 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setStep(2)}
                  disabled={busy}
                >
                  <ChevronLeft className="h-4 w-4" />
                  上一步
                </Button>
                <Button
                  type="button"
                  onClick={() => setStep(4)}
                  disabled={busy || assets.length === 0}
                >
                  下一步
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}

          {!showBootSpinner && step === 4 && packId && (
            <div className="space-y-4">
              <p className="text-sm text-stone-600">
                已通过的 packshot：{approvedPackshots} 张
                {approvedPackshots < 1 ? (
                  <span className="ml-2 text-amber-700">
                    （提交前请至少通过 1 张类型为 packshot 的素材）
                  </span>
                ) : null}
              </p>
              <ul className="max-h-48 space-y-1 overflow-y-auto text-sm text-stone-600">
                {assets.map((a) => (
                  <li key={a.id} className="flex justify-between gap-2">
                    <span className="truncate">{a.type}</span>
                    <span>{a.approval_status}</span>
                  </li>
                ))}
              </ul>
              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setStep(3)}
                  disabled={busy}
                >
                  <ChevronLeft className="h-4 w-4" />
                  上一步
                </Button>
                <Button
                  type="button"
                  onClick={submitPack}
                  disabled={busy || approvedPackshots < 1}
                >
                  {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                  提交审核
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
