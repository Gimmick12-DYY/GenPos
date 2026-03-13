"use client";

import { useState } from "react";
import { ClipboardCheck, Filter, Search } from "lucide-react";
import { NotePackageCard } from "@/components/note-package-card";
import { cn } from "@/lib/utils";

const tabs = [
  { key: "pending", label: "待审核", count: 5 },
  { key: "approved", label: "已通过", count: 12 },
  { key: "rejected", label: "已拒绝", count: 3 },
] as const;

type TabKey = (typeof tabs)[number]["key"];

const reviewItems = [
  {
    title: "秋冬必备！这款面霜让我的脸蛋嫩得像剥了壳的鸡蛋🥚",
    score: 90,
    styleFamily: "治愈系插画",
    complianceStatus: "pending" as const,
    likes: 0,
    comments: 0,
  },
  {
    title: "30天瘦10斤！我的减脂食谱大公开📋",
    score: 82,
    styleFamily: "可爱Q版生活场景",
    complianceStatus: "pending" as const,
    likes: 0,
    comments: 0,
  },
  {
    title: "学生党平价好物｜100元以内的护肤清单💰",
    score: 88,
    styleFamily: "手账贴纸风",
    complianceStatus: "pending" as const,
    likes: 0,
    comments: 0,
  },
  {
    title: "职场穿搭｜通勤一周不重样的极简衣橱👔",
    score: 85,
    styleFamily: "极简软萌插画",
    complianceStatus: "pending" as const,
    likes: 0,
    comments: 0,
  },
  {
    title: "周末探店｜藏在巷子里的宝藏咖啡馆☕",
    score: 91,
    styleFamily: "轻漫画分镜",
    complianceStatus: "pending" as const,
    likes: 0,
    comments: 0,
  },
];

export default function ReviewPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("pending");

  return (
    <div className="mx-auto max-w-7xl p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-light shadow-sm">
          <ClipboardCheck className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-stone-900">待审核</h1>
          <p className="text-sm text-stone-500">
            审核AI生成的笔记方案，确保符合品牌规范
          </p>
        </div>
      </div>

      {/* Tabs + search bar */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex gap-1 rounded-lg bg-stone-100 p-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
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
              placeholder="搜索笔记..."
              className="h-9 w-60 rounded-lg border border-stone-300 bg-white pl-9 pr-3 text-sm placeholder:text-stone-400 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
          </div>
          <button className="flex h-9 items-center gap-1.5 rounded-lg border border-stone-300 bg-white px-3 text-sm text-stone-600 transition-colors hover:bg-stone-50">
            <Filter className="h-3.5 w-3.5" />
            筛选
          </button>
        </div>
      </div>

      {/* Card grid */}
      {activeTab === "pending" && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {reviewItems.map((item, i) => (
            <NotePackageCard
              key={i}
              title={item.title}
              score={item.score}
              styleFamily={item.styleFamily}
              complianceStatus={item.complianceStatus}
              likes={item.likes}
              comments={item.comments}
              onApprove={() => {}}
              onReject={() => {}}
            />
          ))}
        </div>
      )}

      {activeTab === "approved" && (
        <div className="rounded-xl border border-stone-200 bg-surface-raised p-12 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-50">
            <ClipboardCheck className="h-8 w-8 text-emerald-500" />
          </div>
          <h3 className="text-lg font-semibold text-stone-900">已通过审核</h3>
          <p className="mt-1 text-sm text-stone-500">
            共12条笔记已通过审核，可在投放中心管理
          </p>
        </div>
      )}

      {activeTab === "rejected" && (
        <div className="rounded-xl border border-stone-200 bg-surface-raised p-12 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-50">
            <ClipboardCheck className="h-8 w-8 text-red-400" />
          </div>
          <h3 className="text-lg font-semibold text-stone-900">已拒绝</h3>
          <p className="mt-1 text-sm text-stone-500">
            共3条笔记未通过审核，可修改后重新提交
          </p>
        </div>
      )}
    </div>
  );
}
