import { Factory, Search, Filter, MoreHorizontal } from "lucide-react";
import { StatusBadge } from "@/components/ui/badge";

const factoryItems = [
  {
    id: "NP-2024-001",
    title: "秋冬面霜种草笔记",
    product: "水光精华液",
    style: "治愈系插画",
    status: "passed" as const,
    createdAt: "2024-01-15",
    score: 92,
  },
  {
    id: "NP-2024-002",
    title: "学生党平价护肤清单",
    product: "氨基酸洁面乳",
    style: "手账贴纸风",
    status: "pending" as const,
    createdAt: "2024-01-14",
    score: 85,
  },
  {
    id: "NP-2024-003",
    title: "通勤妆容教程分享",
    product: "防晒霜 SPF50+",
    style: "轻漫画分镜",
    status: "review_needed" as const,
    createdAt: "2024-01-14",
    score: 78,
  },
  {
    id: "NP-2024-004",
    title: "周末居家护肤流程",
    product: "玻尿酸面膜",
    style: "可爱Q版生活场景",
    status: "passed" as const,
    createdAt: "2024-01-13",
    score: 89,
  },
  {
    id: "NP-2024-005",
    title: "敏感肌换季指南",
    product: "烟酰胺精华水",
    style: "极简软萌插画",
    status: "draft" as const,
    createdAt: "2024-01-13",
    score: 0,
  },
];

export default function FactoryPage() {
  return (
    <div className="mx-auto max-w-7xl p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-light shadow-sm">
          <Factory className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-stone-900">内容工厂</h1>
          <p className="text-sm text-stone-500">
            查看和管理所有生成的笔记内容
          </p>
        </div>
      </div>

      {/* Toolbar */}
      <div className="mb-6 flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
          <input
            type="text"
            placeholder="搜索笔记..."
            className="h-9 w-full rounded-lg border border-stone-300 bg-white pl-9 pr-3 text-sm placeholder:text-stone-400 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
          />
        </div>
        <button className="flex h-9 items-center gap-1.5 rounded-lg border border-stone-300 bg-white px-3 text-sm text-stone-600 hover:bg-stone-50">
          <Filter className="h-3.5 w-3.5" />
          筛选
        </button>
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-xl border border-stone-200 bg-surface-raised">
        <table className="w-full">
          <thead>
            <tr className="border-b border-stone-200 bg-stone-50/50">
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                编号
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                标题
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                产品
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                风格
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                评分
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                状态
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">
                创建日期
              </th>
              <th className="w-10 px-3 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-100">
            {factoryItems.map((item) => (
              <tr
                key={item.id}
                className="transition-colors hover:bg-stone-50/50"
              >
                <td className="px-5 py-3.5 text-xs font-mono text-stone-400">
                  {item.id}
                </td>
                <td className="px-5 py-3.5 text-sm font-medium text-stone-900">
                  {item.title}
                </td>
                <td className="px-5 py-3.5 text-sm text-stone-600">
                  {item.product}
                </td>
                <td className="px-5 py-3.5">
                  <span className="inline-block rounded-md bg-stone-100 px-2 py-0.5 text-xs text-stone-600">
                    {item.style}
                  </span>
                </td>
                <td className="px-5 py-3.5 text-sm font-semibold text-stone-900">
                  {item.score || "—"}
                </td>
                <td className="px-5 py-3.5">
                  <StatusBadge status={item.status} />
                </td>
                <td className="px-5 py-3.5 text-sm text-stone-500">
                  {item.createdAt}
                </td>
                <td className="px-3 py-3.5">
                  <button className="rounded p-1 text-stone-400 hover:bg-stone-100 hover:text-stone-600">
                    <MoreHorizontal className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
