"use client";

import { Shield, Plus, Pencil } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

const ruleCategories = [
  {
    title: "品牌用语规范",
    description: "定义品牌专属用语和表达方式",
    rules: ["品牌名称统一使用「GenPos」", "产品线名称不可缩写", "禁止使用竞品名称"],
    count: 12,
  },
  {
    title: "合规禁用词",
    description: "平台和法规要求的禁用词列表",
    rules: ["禁止功效性绝对化用语", "禁止虚假促销信息", "禁止医疗功效宣称"],
    count: 48,
  },
  {
    title: "视觉规范",
    description: "品牌视觉标准和图片要求",
    rules: ["封面图必须包含品牌水印", "色调符合品牌调性", "禁止使用未授权素材"],
    count: 8,
  },
  {
    title: "内容调性",
    description: "笔记内容的调性和风格要求",
    rules: ["保持温暖亲切的语气", "避免过度营销感", "强调真实使用体验"],
    count: 15,
  },
];

export default function RulesPage() {
  return (
    <div className="mx-auto max-w-5xl p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-light shadow-sm">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-stone-900">品牌规则</h1>
            <p className="text-sm text-stone-500">
              管理品牌规范，AI生成内容时自动遵守
            </p>
          </div>
        </div>
        <button className="flex h-10 items-center gap-2 rounded-lg bg-primary px-4 text-sm font-medium text-white shadow-sm transition-colors hover:bg-primary-dark">
          <Plus className="h-4 w-4" />
          添加规则
        </button>
      </div>

      {/* Rule category cards */}
      <div className="space-y-4">
        {ruleCategories.map((category, i) => (
          <Card key={i}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-semibold text-stone-900">
                    {category.title}
                  </h3>
                  <p className="mt-0.5 text-sm text-stone-500">
                    {category.description}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="rounded-full bg-stone-100 px-2.5 py-0.5 text-xs font-medium text-stone-600">
                    {category.count} 条规则
                  </span>
                  <button className="rounded-lg p-2 text-stone-400 transition-colors hover:bg-stone-100 hover:text-stone-600">
                    <Pencil className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {category.rules.map((rule, j) => (
                  <li key={j} className="flex items-start gap-2.5 text-sm text-stone-600">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/60" />
                    {rule}
                  </li>
                ))}
              </ul>
              <button className="mt-3 text-xs font-medium text-primary hover:text-primary-dark transition-colors">
                查看全部规则 →
              </button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
