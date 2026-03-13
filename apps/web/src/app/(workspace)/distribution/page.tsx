import { Send, Calendar, Clock, CheckCircle2, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

const distributionStats = [
  { label: "投放中", value: "8", icon: Send, color: "text-primary bg-primary/10" },
  { label: "排期中", value: "5", icon: Calendar, color: "text-blue-500 bg-blue-50" },
  { label: "已完成", value: "42", icon: CheckCircle2, color: "text-emerald-500 bg-emerald-50" },
  { label: "异常", value: "1", icon: AlertCircle, color: "text-amber-500 bg-amber-50" },
];

const scheduledItems = [
  { title: "面霜种草系列 #1", platform: "小红书", time: "今天 18:00", status: "ready" },
  { title: "面霜种草系列 #2", platform: "小红书", time: "明天 12:00", status: "ready" },
  { title: "洁面乳测评笔记", platform: "小红书", time: "明天 18:00", status: "pending" },
  { title: "防晒好物推荐", platform: "小红书", time: "01/18 12:00", status: "ready" },
  { title: "周末护肤流程", platform: "小红书", time: "01/19 10:00", status: "pending" },
];

export default function DistributionPage() {
  return (
    <div className="mx-auto max-w-7xl p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-light shadow-sm">
          <Send className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-stone-900">投放中心</h1>
          <p className="text-sm text-stone-500">
            管理笔记发布排期和投放状态
          </p>
        </div>
      </div>

      {/* Stats */}
      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {distributionStats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardContent className="flex items-center gap-4 py-5">
                <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${stat.color}`}>
                  <Icon className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-stone-900">{stat.value}</p>
                  <p className="text-sm text-stone-500">{stat.label}</p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Schedule list */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-stone-900">发布排期</h3>
            <button className="text-sm font-medium text-primary hover:text-primary-dark transition-colors">
              查看日历视图
            </button>
          </div>
        </CardHeader>
        <CardContent className="px-0 py-0">
          <div className="divide-y divide-stone-100">
            {scheduledItems.map((item, i) => (
              <div key={i} className="flex items-center justify-between px-5 py-4 hover:bg-stone-50/50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className={`h-2 w-2 rounded-full ${item.status === "ready" ? "bg-emerald-400" : "bg-amber-400"}`} />
                  <div>
                    <p className="text-sm font-medium text-stone-900">{item.title}</p>
                    <p className="text-xs text-stone-500">{item.platform}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-sm text-stone-500">
                  <Clock className="h-3.5 w-3.5" />
                  {item.time}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
