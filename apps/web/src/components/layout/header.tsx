"use client";

import { usePathname } from "next/navigation";
import { Bell, Settings } from "lucide-react";
import { cn } from "@/lib/utils";

const routeTitles: Record<string, string> = {
  "/dashboard": "今日推荐",
  "/generate": "一键生成",
  "/chat": "AI对话",
  "/products": "我的产品库",
  "/factory": "内容工厂",
  "/review": "待审核",
  "/distribution": "投放中心",
  "/creators": "达人合作",
  "/analytics": "成效分析",
  "/rules": "品牌规则",
};

export function Header() {
  const pathname = usePathname();
  const title = routeTitles[pathname] || "GenPos";

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-stone-200 bg-surface-raised px-6">
      <h2 className="text-lg font-semibold text-stone-900">{title}</h2>

      <div className="flex items-center gap-2">
        <button className="relative rounded-lg p-2 text-stone-400 transition-colors hover:bg-stone-100 hover:text-stone-600">
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-primary" />
        </button>
        <button className="rounded-lg p-2 text-stone-400 transition-colors hover:bg-stone-100 hover:text-stone-600">
          <Settings className="h-5 w-5" />
        </button>
        <div className="ml-2 h-8 w-px bg-stone-200" />
        <button className="flex items-center gap-2.5 rounded-lg py-1.5 pl-2 pr-3 transition-colors hover:bg-stone-100">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-primary-light to-primary text-sm font-bold text-white">
            U
          </div>
          <span className="text-sm font-medium text-stone-700">用户</span>
        </button>
      </div>
    </header>
  );
}
