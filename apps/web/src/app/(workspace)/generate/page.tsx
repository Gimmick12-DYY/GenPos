"use client";

import { useForm, Controller } from "react-hook-form";
import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { Wand2, Sparkles, Loader2, Leaf, Gift, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Toggle } from "@/components/ui/toggle";
import { TagInput } from "@/components/ui/tag-input";
import { NotePackageCard } from "@/components/note-package-card";
import { PageHeader, PageShell } from "@/components/layout/page-shell";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { ensureAuth, getMerchantId } from "@/lib/auth";

const FORM_STORAGE_KEY = "genpos_generate_draft_v1";

interface GenerateFormData {
  product: string;
  industry: string;
  targetAudience: string;
  targetScenario: string;
  objective: string;
  juguang: boolean;
  pugongying: boolean;
  style: string;
  tone: string;
  bannedWords: string[];
  requiredSellingPoints: string[];
  showPrice: boolean;
  ctaType: string;
}

interface ProductOption {
  id: string;
  name: string;
}

interface ProductListResponse {
  items: Array<{ id: string; name: string; status: string }>;
  total: number;
  limit: number;
  offset: number;
}

interface GenerationAsyncStart {
  mode: "async";
  generation_job_id: string;
  workflow_id: string;
  run_id: string;
  status: string;
}

interface GenerationJobResponse {
  id: string;
  status: string;
}

interface ReviewQueueItem {
  id: string;
  generation_job_id?: string | null;
  style_family?: string | null;
  ranking_score?: number | null;
  compliance_status: string;
  review_status: string;
}

interface ReviewQueueResponse {
  items: ReviewQueueItem[];
  total: number;
}

interface GenerationSyncResult {
  generation_job_id?: string;
  note_package_id?: string;
  error?: string;
  pipeline_log?: unknown;
}

function buildSpecialInstructions(data: GenerateFormData): string {
  const parts: string[] = [];
  if (data.industry.trim()) parts.push(`行业：${data.industry.trim()}`);
  if (data.targetScenario.trim()) parts.push(`场景：${data.targetScenario.trim()}`);
  parts.push(`语气风格：${data.tone}`);
  if (data.bannedWords.length)
    parts.push(`禁用词（勿出现）：${data.bannedWords.join("、")}`);
  if (data.requiredSellingPoints.length)
    parts.push(`必须提及的卖点：${data.requiredSellingPoints.join("、")}`);
  parts.push(`CTA 导向：${data.ctaType}`);
  parts.push(data.showPrice ? "笔记中可体现价格或价位感。" : "不要在正文中写具体价格数字。");
  return parts.join("\n");
}

function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
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

const objectives = [
  { value: "种草", label: "种草", emoji: "🌱" },
  { value: "转化", label: "转化", emoji: "💰" },
  { value: "品宣", label: "品宣", emoji: "📣" },
  { value: "互动", label: "互动", emoji: "💬" },
];

const styleFamilies = [
  {
    value: "治愈系插画",
    label: "治愈系插画",
    preview: "🎨",
    description: "温暖柔和的手绘风格",
  },
  {
    value: "轻漫画分镜",
    label: "轻漫画分镜",
    preview: "📖",
    description: "分格叙事，故事感强",
  },
  {
    value: "可爱Q版生活场景",
    label: "Q版生活场景",
    preview: "🧸",
    description: "可爱卡通，贴近生活",
  },
  {
    value: "手账贴纸风",
    label: "手账贴纸风",
    preview: "📝",
    description: "精致拼贴，元素丰富",
  },
  {
    value: "极简软萌插画",
    label: "极简软萌插画",
    preview: "✨",
    description: "简洁线条，软萌治愈",
  },
];

const toneOptions = [
  { value: "温柔种草", label: "温柔种草" },
  { value: "闺蜜安利", label: "闺蜜安利" },
  { value: "专业测评", label: "专业测评" },
  { value: "搞笑吐槽", label: "搞笑吐槽" },
  { value: "文艺清新", label: "文艺清新" },
  { value: "干货分享", label: "干货分享" },
];

const ctaOptions = [
  { value: "收藏", label: "收藏" },
  { value: "关注", label: "关注" },
  { value: "评论", label: "评论" },
  { value: "私信", label: "私信" },
  { value: "购买链接", label: "购买链接" },
];

const defaultForm: GenerateFormData = {
  product: "",
  industry: "",
  targetAudience: "",
  targetScenario: "",
  objective: "种草",
  juguang: false,
  pugongying: false,
  style: "治愈系插画",
  tone: "温柔种草",
  bannedWords: [],
  requiredSellingPoints: [],
  showPrice: false,
  ctaType: "收藏",
};

export default function GeneratePage() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [products, setProducts] = useState<ProductOption[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);
  const [productsError, setProductsError] = useState<string | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [createdPackage, setCreatedPackage] = useState<ReviewQueueItem | null>(
    null
  );
  const [pollMessage, setPollMessage] = useState<string | null>(null);
  const [resultInfo, setResultInfo] = useState<string | null>(null);

  const { register, control, handleSubmit, watch, setValue, reset } =
    useForm<GenerateFormData>({
      defaultValues: defaultForm,
    });

  const selectedObjective = watch("objective");
  const selectedStyle = watch("style");

  useEffect(() => {
    ensureAuth()
      .then(() => setAuthReady(true))
      .catch((e) => setAuthError(e instanceof Error ? e.message : "认证失败"));
  }, []);

  useEffect(() => {
    if (!authReady) return;
    const merchantId = getMerchantId();
    if (!merchantId) {
      setProductsLoading(false);
      return;
    }
    setProductsLoading(true);
    api
      .get<ProductListResponse>(
        `/merchants/${merchantId}/products?limit=100&offset=0`
      )
      .then((res) => {
        setProducts(
          res.items
            .filter((p) => p.status === "active" || p.status === "paused")
            .map((p) => ({ id: p.id, name: p.name }))
        );
        setProductsError(null);
      })
      .catch((e) =>
        setProductsError(
          e instanceof Error ? e.message : "加载产品列表失败"
        )
      )
      .finally(() => setProductsLoading(false));
  }, [authReady]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const raw = sessionStorage.getItem(FORM_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<GenerateFormData>;
        reset({ ...defaultForm, ...parsed });
      }
    } catch {
      /* ignore */
    }
  }, [reset]);

  useEffect(() => {
    const sub = watch((data) => {
      try {
        sessionStorage.setItem(FORM_STORAGE_KEY, JSON.stringify(data));
      } catch {
        /* quota / private mode */
      }
    });
    return () => sub.unsubscribe();
  }, [watch]);

  const applyPreset = useCallback(
    (preset: Partial<GenerateFormData>) => {
      Object.entries(preset).forEach(([k, v]) => {
        if (v !== undefined) {
          setValue(k as keyof GenerateFormData, v as never, {
            shouldDirty: true,
          });
        }
      });
    },
    [setValue]
  );

  async function pollUntilJobComplete(
    jobId: string
  ): Promise<ReviewQueueItem | null> {
    const maxAttempts = 180;
    for (let i = 0; i < maxAttempts; i++) {
      const job = await api.get<GenerationJobResponse>(
        `/generate/jobs/${jobId}`
      );
      if (job.status === "failed") {
        throw new Error("生成任务失败，请查看 API 日志或稍后重试。");
      }
      if (job.status === "completed") {
        const queue = await api.get<ReviewQueueResponse>(
          `/review/queue?limit=30&offset=0`
        );
        const match = queue.items.find(
          (p) => p.generation_job_id === jobId
        );
        return match ?? null;
      }
      await sleep(2000);
    }
    throw new Error("生成超时（超过约 6 分钟）。请稍后在「待审核」查看是否已完成。");
  }

  async function onSubmit(data: GenerateFormData) {
    setSubmitError(null);
    setCreatedPackage(null);
    setPollMessage(null);
    setResultInfo(null);

    if (!data.product) {
      setSubmitError("请选择一个产品。");
      return;
    }

    setIsGenerating(true);
    try {
      await ensureAuth();
      const persona =
        [data.targetAudience, data.tone].filter(Boolean).join(" · ") || "";

      const body = {
        product_id: data.product,
        objective: data.objective,
        persona: persona || undefined,
        style_preference: data.style.slice(0, 64),
        special_instructions: buildSpecialInstructions(data),
        is_juguang: data.juguang,
        is_pugongying: data.pugongying,
      };

      const res = await api.post<GenerationAsyncStart | GenerationSyncResult>(
        "/generate/request",
        body
      );

      if (
        res &&
        typeof res === "object" &&
        "mode" in res &&
        (res as GenerationAsyncStart).mode === "async"
      ) {
        const asyncRes = res as GenerationAsyncStart;
        setPollMessage("任务已排队，正在生成，请稍候…");
        try {
          const pkg = await pollUntilJobComplete(asyncRes.generation_job_id);
          setPollMessage(null);
          if (pkg) {
            setCreatedPackage(pkg);
          } else {
            setResultInfo(
              "生成已完成。若未在此显示卡片，请到「待审核」查看最新笔记包。"
            );
          }
        } catch (pollErr) {
          setPollMessage(null);
          throw pollErr;
        }
        return;
      }

      const sync = res as GenerationSyncResult;
      if (sync.error) {
        setSubmitError(sync.error);
        return;
      }
      if (sync.note_package_id) {
        const queue = await api.get<ReviewQueueResponse>(
          `/review/queue?limit=30&offset=0`
        );
        const pkg =
          queue.items.find(
            (p) => p.id === sync.note_package_id
          ) ?? null;
        if (pkg) setCreatedPackage(pkg);
        else {
          setCreatedPackage({
            id: sync.note_package_id,
            generation_job_id: sync.generation_job_id ?? null,
            style_family: null,
            ranking_score: null,
            compliance_status: "pending",
            review_status: "pending",
          });
        }
      }
    } catch (e) {
      setSubmitError(
        e instanceof Error ? e.message : "生成失败，请稍后重试。"
      );
    } finally {
      setIsGenerating(false);
    }
  }

  if (authError && !authReady) {
    return (
      <PageShell className="max-w-5xl">
        <div className="rounded-2xl border border-red-200/80 bg-red-50 p-8 text-center text-sm text-red-900 shadow-sm">
          <p className="font-medium">无法继续</p>
          <p className="mt-1">{authError}</p>
        </div>
      </PageShell>
    );
  }

  const productSelectOptions = [
    { value: "", label: productsLoading ? "加载产品中…" : "请选择产品" },
    ...products.map((p) => ({ value: p.id, label: p.name })),
  ];

  return (
    <PageShell className="max-w-5xl">
      <PageHeader
        icon={Wand2}
        title="一键生成"
        description="配置参数，AI 为您生成完整的小红书笔记方案"
      />

      {createdPackage && (
        <div className="mb-8 rounded-2xl border border-emerald-200/80 bg-emerald-50/90 p-6 shadow-sm">
          <p className="mb-4 text-sm font-medium text-emerald-900">
            已生成笔记方案，可在此快速预览或前往待审核处理
          </p>
          <div className="max-w-sm">
            <NotePackageCard
              title={
                createdPackage.style_family
                  ? `笔记 · ${createdPackage.style_family}`
                  : "新笔记方案"
              }
              score={
                createdPackage.ranking_score != null
                  ? Math.round(createdPackage.ranking_score)
                  : undefined
              }
              styleFamily={createdPackage.style_family ?? undefined}
              complianceStatus={complianceToCardStatus(
                createdPackage.compliance_status
              )}
            />
          </div>
          <Link
            href="/review"
            className="mt-4 inline-block text-sm font-medium text-primary hover:underline"
          >
            前往待审核 →
          </Link>
        </div>
      )}

      {submitError && (
        <div className="mb-6 rounded-2xl border border-red-200/80 bg-red-50 px-4 py-3 text-sm text-red-900 shadow-sm">
          {submitError}
        </div>
      )}

      {productsError && (
        <div className="mb-6 rounded-2xl border border-amber-200/80 bg-amber-50 px-4 py-3 text-sm text-amber-950 shadow-sm">
          产品列表加载失败：{productsError}
        </div>
      )}

      {authReady && !productsLoading && products.length === 0 && !productsError && (
        <div className="mb-6 rounded-2xl border border-stone-200/80 bg-stone-50 px-4 py-3 text-sm text-stone-800 shadow-sm">
          还没有可用产品。请先到「
          <Link href="/products" className="font-medium text-primary underline">
            我的产品库
          </Link>
          」添加商品后再生成笔记。
        </div>
      )}

      {resultInfo && (
        <div className="mb-6 rounded-2xl border border-emerald-200/80 bg-emerald-50/90 px-4 py-3 text-sm text-emerald-950 shadow-sm">
          {resultInfo}{" "}
          <Link href="/review" className="font-medium text-primary underline">
            去待审核
          </Link>
        </div>
      )}

      <div className="mb-6 flex flex-wrap gap-2">
        <span className="w-full text-xs font-medium text-stone-500">
          快速模板
        </span>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          className="gap-1"
          onClick={() =>
            applyPreset({
              objective: "种草",
              targetScenario: "节日大促、限时好礼、礼盒装心智",
              tone: "闺蜜安利",
              ctaType: "收藏",
            })
          }
        >
          <Gift className="h-4 w-4" />
          节日促销
        </Button>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          className="gap-1"
          onClick={() =>
            applyPreset({
              objective: "品宣",
              targetScenario: "新品上市、成分/卖点首秀",
              tone: "专业测评",
              requiredSellingPoints: ["新品", "核心成分"],
            })
          }
        >
          <Sparkles className="h-4 w-4" />
          新品上架
        </Button>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          className="gap-1"
          onClick={() =>
            applyPreset({
              objective: "互动",
              targetScenario: "真实使用反馈、复购理由",
              tone: "温柔种草",
              ctaType: "评论",
            })
          }
        >
          <Star className="h-4 w-4" />
          用户好评
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="gap-1"
          onClick={() => reset(defaultForm)}
        >
          <Leaf className="h-4 w-4" />
          重置表单
        </Button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          <div className="space-y-6">
            <div className="rounded-2xl border border-stone-200/80 bg-surface-raised p-6 shadow-sm">
              <h3 className="mb-5 text-base font-semibold text-stone-900">
                基础设置
              </h3>
              <div className="space-y-5">
                <Select
                  label="产品"
                  options={productSelectOptions}
                  {...register("product", { required: true })}
                />
                <Input
                  label="行业"
                  placeholder="例：护肤美妆、家居、食品"
                  {...register("industry")}
                />
                <Input
                  label="目标人群"
                  placeholder="例：25-35岁敏感肌女性"
                  {...register("targetAudience")}
                />
                <Input
                  label="目标场景"
                  placeholder="例：换季护肤、日常通勤"
                  {...register("targetScenario")}
                />

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-stone-700">
                    发布目的
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {objectives.map((obj) => (
                      <label
                        key={obj.value}
                        className={cn(
                          "flex cursor-pointer items-center gap-2 rounded-lg border-2 px-4 py-3 text-sm font-medium transition-all",
                          selectedObjective === obj.value
                            ? "border-primary bg-primary/5 text-primary-dark"
                            : "border-stone-200 text-stone-600 hover:border-stone-300"
                        )}
                      >
                        <input
                          type="radio"
                          value={obj.value}
                          {...register("objective")}
                          className="sr-only"
                        />
                        <span className="text-lg">{obj.emoji}</span>
                        {obj.label}
                      </label>
                    ))}
                  </div>
                </div>

                <div className="space-y-4 rounded-lg bg-stone-50 p-4">
                  <Controller
                    name="juguang"
                    control={control}
                    render={({ field }) => (
                      <Toggle
                        checked={field.value}
                        onChange={field.onChange}
                        label="是否投聚光"
                        description="开启后将优化笔记的投放适配度"
                      />
                    )}
                  />
                  <Controller
                    name="pugongying"
                    control={control}
                    render={({ field }) => (
                      <Toggle
                        checked={field.value}
                        onChange={field.onChange}
                        label="是否做蒲公英合作"
                        description="适配达人合作的内容结构"
                      />
                    )}
                  />
                  <Controller
                    name="showPrice"
                    control={control}
                    render={({ field }) => (
                      <Toggle
                        checked={field.value}
                        onChange={field.onChange}
                        label="是否带价格"
                        description="在笔记中展示产品价格信息"
                      />
                    )}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-2xl border border-stone-200/80 bg-surface-raised p-6 shadow-sm">
              <h3 className="mb-5 text-base font-semibold text-stone-900">
                风格选择
              </h3>
              <div className="grid grid-cols-1 gap-2">
                {styleFamilies.map((style) => (
                  <label
                    key={style.value}
                    className={cn(
                      "flex cursor-pointer items-center gap-3 rounded-lg border-2 px-4 py-3 transition-all",
                      selectedStyle === style.value
                        ? "border-primary bg-primary/5"
                        : "border-stone-200 hover:border-stone-300"
                    )}
                  >
                    <input
                      type="radio"
                      value={style.value}
                      {...register("style")}
                      className="sr-only"
                    />
                    <span className="text-2xl">{style.preview}</span>
                    <div className="min-w-0">
                      <p
                        className={cn(
                          "text-sm font-medium",
                          selectedStyle === style.value
                            ? "text-primary-dark"
                            : "text-stone-700"
                        )}
                      >
                        {style.label}
                      </p>
                      <p className="text-xs text-stone-500">
                        {style.description}
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-stone-200/80 bg-surface-raised p-6 shadow-sm">
              <h3 className="mb-5 text-base font-semibold text-stone-900">
                内容调整
              </h3>
              <div className="space-y-5">
                <Select
                  label="语气"
                  options={toneOptions}
                  {...register("tone")}
                />
                <Select
                  label="CTA类型"
                  options={ctaOptions}
                  {...register("ctaType")}
                />
                <Controller
                  name="bannedWords"
                  control={control}
                  render={({ field }) => (
                    <TagInput
                      label="禁用词"
                      value={field.value}
                      onChange={field.onChange}
                      placeholder="输入禁用词后按回车添加"
                    />
                  )}
                />
                <Controller
                  name="requiredSellingPoints"
                  control={control}
                  render={({ field }) => (
                    <TagInput
                      label="必须出现的卖点"
                      value={field.value}
                      onChange={field.onChange}
                      placeholder="输入卖点后按回车添加"
                    />
                  )}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 flex flex-col items-center gap-2">
          {pollMessage && (
            <p className="text-sm text-stone-600">{pollMessage}</p>
          )}
          <Button
            type="submit"
            size="lg"
            disabled={isGenerating || !authReady}
            className="min-w-[240px] text-base shadow-lg shadow-primary/25"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                AI生成中...
              </>
            ) : (
              <>
                <Sparkles className="h-5 w-5" />
                一键生成笔记方案
              </>
            )}
          </Button>
        </div>
      </form>
    </PageShell>
  );
}
