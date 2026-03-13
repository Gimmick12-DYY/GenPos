import { Users, Search, Star, ExternalLink } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const creators = [
  { name: "小美美妆日记", followers: "12.5万", category: "美妆", matchScore: 95, status: "合作中" },
  { name: "生活研究所", followers: "8.3万", category: "生活", matchScore: 88, status: "待联系" },
  { name: "护肤小课堂", followers: "23.1万", category: "护肤", matchScore: 92, status: "合作中" },
  { name: "每日穿搭灵感", followers: "5.6万", category: "穿搭", matchScore: 78, status: "待联系" },
  { name: "减脂干货铺", followers: "15.8万", category: "健身", matchScore: 72, status: "已完成" },
  { name: "探店小达人", followers: "9.2万", category: "探店", matchScore: 85, status: "待联系" },
];

export default function CreatorsPage() {
  return (
    <div className="mx-auto max-w-7xl p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-light shadow-sm">
          <Users className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-stone-900">达人合作</h1>
          <p className="text-sm text-stone-500">
            发现和管理蒲公英达人合作关系
          </p>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6 relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
        <input
          type="text"
          placeholder="搜索达人..."
          className="h-10 w-full max-w-md rounded-lg border border-stone-300 bg-white pl-9 pr-3 text-sm placeholder:text-stone-400 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
        />
      </div>

      {/* Creator grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {creators.map((creator, i) => (
          <Card key={i} className="cursor-pointer">
            <CardContent className="py-5">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-pink-100 to-rose-200">
                    <span className="text-lg font-bold text-rose-500">
                      {creator.name[0]}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-stone-900">{creator.name}</h3>
                    <p className="text-xs text-stone-500">{creator.followers} 粉丝 · {creator.category}</p>
                  </div>
                </div>
                <ExternalLink className="h-4 w-4 text-stone-400" />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4 text-amber-400 fill-amber-400" />
                  <span className="text-sm font-semibold text-stone-900">匹配度 {creator.matchScore}%</span>
                </div>
                <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  creator.status === "合作中"
                    ? "bg-emerald-50 text-emerald-700"
                    : creator.status === "已完成"
                      ? "bg-stone-100 text-stone-600"
                      : "bg-blue-50 text-blue-700"
                }`}>
                  {creator.status}
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
