"use client";

import { Bell, Settings } from "lucide-react";

export function Header() {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-stone-200/80 bg-surface-raised/85 px-5 backdrop-blur-xl supports-[backdrop-filter]:bg-surface-raised/70 lg:h-16 lg:px-8">
      <div className="flex min-w-0 items-center gap-3">
        <div
          className="hidden h-8 w-1 shrink-0 rounded-full bg-gradient-to-b from-primary to-primary-light sm:block"
          aria-hidden
        />
        <p className="text-xs font-medium text-stone-400">
          当前工作区 · 单商户实例（数据与登录商户绑定）
        </p>
      </div>

      <div className="flex items-center gap-1">
        <button
          type="button"
          className="relative rounded-xl p-2.5 text-stone-400 transition-colors hover:bg-stone-100 hover:text-stone-700"
          aria-label="通知"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-primary ring-2 ring-white" />
        </button>
        <button
          type="button"
          className="rounded-xl p-2.5 text-stone-400 transition-colors hover:bg-stone-100 hover:text-stone-700"
          aria-label="设置"
        >
          <Settings className="h-5 w-5" />
        </button>
        <div className="mx-1 hidden h-8 w-px bg-stone-200 sm:block" />
        <button
          type="button"
          className="flex items-center gap-2.5 rounded-xl py-1.5 pl-1.5 pr-2 transition-colors hover:bg-stone-100"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-primary-light to-primary text-sm font-bold text-white shadow-md shadow-primary/25">
            U
          </div>
          <span className="hidden text-sm font-medium text-stone-700 sm:inline">
            用户
          </span>
        </button>
      </div>
    </header>
  );
}
