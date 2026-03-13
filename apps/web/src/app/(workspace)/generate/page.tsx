"use client";

import { useForm, Controller } from "react-hook-form";
import { useState } from "react";
import { Wand2, Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Toggle } from "@/components/ui/toggle";
import { TagInput } from "@/components/ui/tag-input";
import { cn } from "@/lib/utils";

interface GenerateFormData {
  product: string;
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

const productOptions = [
  { value: "", label: "请选择产品" },
  { value: "product-1", label: "水光精华液 30ml" },
  { value: "product-2", label: "氨基酸洁面乳 120g" },
  { value: "product-3", label: "防晒霜 SPF50+ 50ml" },
];

export default function GeneratePage() {
  const [isGenerating, setIsGenerating] = useState(false);
  const { register, control, handleSubmit, watch, setValue } =
    useForm<GenerateFormData>({
      defaultValues: {
        product: "",
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
      },
    });

  const selectedObjective = watch("objective");
  const selectedStyle = watch("style");

  function onSubmit(data: GenerateFormData) {
    setIsGenerating(true);
    // Simulate generation
    setTimeout(() => setIsGenerating(false), 3000);
  }

  return (
    <div className="mx-auto max-w-5xl p-6 lg:p-8">
      {/* Page header */}
      <div className="mb-8 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-light shadow-sm">
          <Wand2 className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-stone-900">一键生成</h1>
          <p className="text-sm text-stone-500">
            配置参数，AI为您生成完整的小红书笔记方案
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          {/* Left column — Core settings */}
          <div className="space-y-6">
            <div className="rounded-xl border border-stone-200 bg-surface-raised p-6">
              <h3 className="mb-5 text-base font-semibold text-stone-900">
                基础设置
              </h3>
              <div className="space-y-5">
                <Select
                  label="产品"
                  options={productOptions}
                  placeholder="请选择产品"
                  {...register("product")}
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

                {/* Objective radio group */}
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
                            : "border-stone-200 text-stone-600 hover:border-stone-300",
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

                {/* Toggle switches */}
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

          {/* Right column — Style & Content settings */}
          <div className="space-y-6">
            {/* Style selector */}
            <div className="rounded-xl border border-stone-200 bg-surface-raised p-6">
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
                        : "border-stone-200 hover:border-stone-300",
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
                            : "text-stone-700",
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

            {/* Content tweaks */}
            <div className="rounded-xl border border-stone-200 bg-surface-raised p-6">
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

        {/* Submit button */}
        <div className="mt-8 flex justify-center">
          <Button
            type="submit"
            size="lg"
            disabled={isGenerating}
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
    </div>
  );
}
