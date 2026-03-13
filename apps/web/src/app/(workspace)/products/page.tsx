import { Package, Plus, Search } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const placeholderProducts = [
  {
    name: "水光精华液 30ml",
    category: "护肤",
    notes: 24,
    image: null,
  },
  {
    name: "氨基酸洁面乳 120g",
    category: "洁面",
    notes: 18,
    image: null,
  },
  {
    name: "防晒霜 SPF50+ 50ml",
    category: "防晒",
    notes: 12,
    image: null,
  },
  {
    name: "玻尿酸面膜 5片装",
    category: "面膜",
    notes: 9,
    image: null,
  },
  {
    name: "烟酰胺精华水 200ml",
    category: "水乳",
    notes: 15,
    image: null,
  },
  {
    name: "修护眼霜 15g",
    category: "眼部",
    notes: 6,
    image: null,
  },
];

export default function ProductsPage() {
  return (
    <div className="mx-auto max-w-7xl p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary-light shadow-sm">
            <Package className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-stone-900">我的产品库</h1>
            <p className="text-sm text-stone-500">
              管理产品信息，关联生成的笔记内容
            </p>
          </div>
        </div>
        <button className="flex h-10 items-center gap-2 rounded-lg bg-primary px-4 text-sm font-medium text-white shadow-sm transition-colors hover:bg-primary-dark">
          <Plus className="h-4 w-4" />
          添加产品
        </button>
      </div>

      {/* Search */}
      <div className="mb-6 relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
        <input
          type="text"
          placeholder="搜索产品名称..."
          className="h-10 w-full max-w-md rounded-lg border border-stone-300 bg-white pl-9 pr-3 text-sm placeholder:text-stone-400 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
        />
      </div>

      {/* Product grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {placeholderProducts.map((product, i) => (
          <Card key={i} className="cursor-pointer transition-shadow hover:shadow-md">
            <CardContent className="flex items-center gap-4 py-5">
              <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-stone-100 to-stone-200">
                <Package className="h-7 w-7 text-stone-400" />
              </div>
              <div className="min-w-0 flex-1">
                <h3 className="truncate text-sm font-semibold text-stone-900">
                  {product.name}
                </h3>
                <p className="mt-0.5 text-xs text-stone-500">
                  {product.category}
                </p>
                <p className="mt-1.5 text-xs text-stone-400">
                  已生成 <span className="font-medium text-primary">{product.notes}</span> 条笔记
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
