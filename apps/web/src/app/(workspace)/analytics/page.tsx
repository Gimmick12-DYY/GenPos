import { BarChart3, TrendingUp, Eye, Heart, MessageCircle, Bookmark } from "lucide-react";
import { PageHeader, PageShell } from "@/components/layout/page-shell";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

const kpis = [
  { label: "总曝光", value: "124.5K", change: "+12.3%", icon: Eye },
  { label: "总互动", value: "8,432", change: "+8.7%", icon: Heart },
  { label: "总评论", value: "1,256", change: "+15.2%", icon: MessageCircle },
  { label: "总收藏", value: "3,891", change: "+6.4%", icon: Bookmark },
];

const topNotes = [
  { title: "黄皮天花板色号推荐💄", views: "45.2K", likes: "3,400", rate: "7.5%" },
  { title: "租房改造300块ins风✨", views: "38.1K", likes: "2,100", rate: "5.5%" },
  { title: "露营装备清单🏕️", views: "28.9K", likes: "1,890", rate: "6.5%" },
  { title: "敏感肌救星精华液🌿", views: "22.3K", likes: "1,240", rate: "5.6%" },
  { title: "打工人减脂便当🍱", views: "15.6K", likes: "890", rate: "5.7%" },
];

export default function AnalyticsPage() {
  return (
    <PageShell>
      <PageHeader
        icon={BarChart3}
        title="成效分析"
        description="查看内容表现数据和投放效果分析"
      />

      {/* KPI cards */}
      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <Card key={kpi.label}>
              <CardContent className="py-5">
                <div className="flex items-center justify-between mb-3">
                  <Icon className="h-5 w-5 text-stone-400" />
                  <span className="flex items-center gap-1 text-xs font-medium text-emerald-600">
                    <TrendingUp className="h-3 w-3" />
                    {kpi.change}
                  </span>
                </div>
                <p className="text-2xl font-bold text-stone-900">{kpi.value}</p>
                <p className="text-sm text-stone-500">{kpi.label}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Chart placeholder */}
      <Card className="mb-8">
        <CardHeader>
          <h3 className="text-base font-semibold text-stone-900">趋势总览</h3>
        </CardHeader>
        <CardContent>
          <div className="flex h-64 items-center justify-center rounded-2xl border border-dashed border-stone-300/80 bg-stone-50/80">
            <div className="text-center">
              <BarChart3 className="mx-auto mb-2 h-10 w-10 text-stone-300" />
              <p className="text-sm text-stone-400">图表区域</p>
              <p className="text-xs text-stone-400">接入数据后自动展示趋势图</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Top notes table */}
      <Card>
        <CardHeader>
          <h3 className="text-base font-semibold text-stone-900">热门笔记 TOP 5</h3>
        </CardHeader>
        <CardContent className="px-0 py-0">
          <table className="w-full">
            <thead>
              <tr className="border-b border-stone-200 bg-stone-50/50">
                <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">排名</th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-stone-500">标题</th>
                <th className="px-5 py-3 text-right text-xs font-medium uppercase tracking-wider text-stone-500">曝光</th>
                <th className="px-5 py-3 text-right text-xs font-medium uppercase tracking-wider text-stone-500">点赞</th>
                <th className="px-5 py-3 text-right text-xs font-medium uppercase tracking-wider text-stone-500">互动率</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {topNotes.map((note, i) => (
                <tr key={i} className="hover:bg-stone-50/50 transition-colors">
                  <td className="px-5 py-3.5">
                    <span className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${
                      i < 3 ? "bg-primary/10 text-primary" : "bg-stone-100 text-stone-500"
                    }`}>
                      {i + 1}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-sm font-medium text-stone-900">{note.title}</td>
                  <td className="px-5 py-3.5 text-right text-sm text-stone-600">{note.views}</td>
                  <td className="px-5 py-3.5 text-right text-sm text-stone-600">{note.likes}</td>
                  <td className="px-5 py-3.5 text-right text-sm font-semibold text-primary">{note.rate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </PageShell>
  );
}
