"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sparkles,
  Wand2,
  MessageSquare,
  Package,
  Factory,
  ClipboardCheck,
  Send,
  Users,
  BarChart3,
  Shield,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";

const navItems = [
  { label: "今日推荐", href: "/dashboard", icon: Sparkles },
  { label: "一键生成", href: "/generate", icon: Wand2 },
  { label: "AI对话", href: "/chat", icon: MessageSquare },
  { label: "我的产品库", href: "/products", icon: Package },
  { label: "内容工厂", href: "/factory", icon: Factory },
  { label: "待审核", href: "/review", icon: ClipboardCheck },
  { label: "投放中心", href: "/distribution", icon: Send },
  { label: "达人合作", href: "/creators", icon: Users },
  { label: "成效分析", href: "/analytics", icon: BarChart3 },
  { label: "品牌规则", href: "/rules", icon: Shield },
] as const;

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "flex h-screen flex-col border-r border-stone-200 bg-surface-raised transition-all duration-300",
        collapsed ? "w-[68px]" : "w-60",
      )}
    >
      {/* Brand */}
      <div className="flex h-16 items-center gap-2.5 border-b border-stone-100 px-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-primary-light shadow-sm">
          <Sparkles className="h-5 w-5 text-white" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <h1 className="truncate text-lg font-bold tracking-tight text-stone-900">
              GenPos
            </h1>
            <p className="truncate text-[10px] leading-tight text-stone-400">
              小红书AI工作台
            </p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href));
            const Icon = item.icon;

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150",
                    isActive
                      ? "bg-primary/10 text-primary-dark"
                      : "text-stone-600 hover:bg-stone-100 hover:text-stone-900",
                    collapsed && "justify-center px-0",
                  )}
                  title={collapsed ? item.label : undefined}
                >
                  <Icon
                    className={cn(
                      "h-[18px] w-[18px] shrink-0 transition-colors",
                      isActive
                        ? "text-primary"
                        : "text-stone-400 group-hover:text-stone-600",
                    )}
                  />
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Collapse toggle */}
      <div className="border-t border-stone-100 p-3">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex w-full items-center justify-center rounded-lg p-2 text-stone-400 transition-colors hover:bg-stone-100 hover:text-stone-600"
        >
          {collapsed ? (
            <PanelLeftOpen className="h-4 w-4" />
          ) : (
            <PanelLeftClose className="h-4 w-4" />
          )}
        </button>
      </div>
    </aside>
  );
}
