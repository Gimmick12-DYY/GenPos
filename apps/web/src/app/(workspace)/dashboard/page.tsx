import { NotePackageCard } from "@/components/note-package-card";
import { Sparkles, TrendingUp, Eye } from "lucide-react";

const placeholderNotes = [
  {
    title: "🌿 这款精华真的救了我的烂脸！敏感肌姐妹快冲",
    score: 92,
    styleFamily: "治愈系插画",
    complianceStatus: "passed" as const,
    likes: 1240,
    comments: 89,
  },
  {
    title: "打工人早餐｜5分钟搞定的减脂便当🍱",
    score: 88,
    styleFamily: "可爱Q版生活场景",
    complianceStatus: "passed" as const,
    likes: 890,
    comments: 56,
  },
  {
    title: "租房改造｜300块打造ins风卧室✨",
    score: 85,
    styleFamily: "手账贴纸风",
    complianceStatus: "review_needed" as const,
    likes: 2100,
    comments: 134,
  },
  {
    title: "黄皮天花板！这个色号我能吹一辈子💄",
    score: 91,
    styleFamily: "轻漫画分镜",
    complianceStatus: "passed" as const,
    likes: 3400,
    comments: 267,
  },
  {
    title: "一周瘦5斤｜懒人居家运动跟练计划",
    score: 79,
    styleFamily: "极简软萌插画",
    complianceStatus: "pending" as const,
    likes: 560,
    comments: 42,
  },
  {
    title: "露营装备清单🏕️新手入门看这一篇就够了",
    score: 87,
    styleFamily: "手账贴纸风",
    complianceStatus: "passed" as const,
    likes: 1890,
    comments: 98,
  },
];

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-7xl p-6 lg:p-8">
      {/* Hero section */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-light shadow-sm">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-stone-900">今日推荐</h1>
            <p className="text-sm text-stone-500">
              基于品牌规则和市场趋势，为您精选的笔记内容方案
            </p>
          </div>
        </div>
      </div>

      {/* Stats row */}
      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="flex items-center gap-4 rounded-xl border border-stone-200 bg-surface-raised p-5">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <div>
            <p className="text-2xl font-bold text-stone-900">6</p>
            <p className="text-sm text-stone-500">今日生成</p>
          </div>
        </div>
        <div className="flex items-center gap-4 rounded-xl border border-stone-200 bg-surface-raised p-5">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10">
            <TrendingUp className="h-6 w-6 text-accent" />
          </div>
          <div>
            <p className="text-2xl font-bold text-stone-900">87.3</p>
            <p className="text-sm text-stone-500">平均评分</p>
          </div>
        </div>
        <div className="flex items-center gap-4 rounded-xl border border-stone-200 bg-surface-raised p-5">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50">
            <Eye className="h-6 w-6 text-blue-500" />
          </div>
          <div>
            <p className="text-2xl font-bold text-stone-900">12.4K</p>
            <p className="text-sm text-stone-500">预估曝光</p>
          </div>
        </div>
      </div>

      {/* Note package grid */}
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-stone-900">推荐笔记方案</h2>
        <button className="text-sm font-medium text-primary hover:text-primary-dark transition-colors">
          查看全部 →
        </button>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {placeholderNotes.map((note, i) => (
          <NotePackageCard
            key={i}
            title={note.title}
            score={note.score}
            styleFamily={note.styleFamily}
            complianceStatus={note.complianceStatus}
            likes={note.likes}
            comments={note.comments}
          />
        ))}
      </div>
    </div>
  );
}
