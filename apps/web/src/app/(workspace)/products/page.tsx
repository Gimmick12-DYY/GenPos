"use client";

import { useEffect, useState } from "react";
import { Package, Plus, Pencil, Loader2, X, Search } from "lucide-react";
import { PageHeader, PageShell } from "@/components/layout/page-shell";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { ensureAuth, getMerchantId } from "@/lib/auth";

interface Product {
  id: string;
  merchant_id: string;
  name: string;
  category: string;
  status: string;
  primary_objective: string | null;
  description: string | null;
}

interface ProductListResponse {
  items: Product[];
  total: number;
  limit: number;
  offset: number;
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState<"add" | "edit" | null>(null);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [saving, setSaving] = useState(false);
  const [formName, setFormName] = useState("");
  const [formCategory, setFormCategory] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [search, setSearch] = useState("");

  const merchantId = getMerchantId();

  async function loadProducts() {
    if (!merchantId) return;
    try {
      const res = await api.get<ProductListResponse>(
        `/merchants/${merchantId}/products?limit=50&offset=0`
      );
      setProducts(res.items || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let cancelled = false;
    (async () => {
      await ensureAuth();
      if (getMerchantId()) {
        await loadProducts();
      } else {
        setLoading(false);
      }
      if (cancelled) return;
    })();
    return () => { cancelled = true; };
  }, [merchantId]);

  function openAdd() {
    setEditingProduct(null);
    setFormName("");
    setFormCategory("床垫");
    setFormDescription("");
    setModalOpen("add");
  }

  function openEdit(p: Product) {
    setEditingProduct(p);
    setFormName(p.name);
    setFormCategory(p.category);
    setFormDescription(p.description || "");
    setModalOpen("edit");
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!merchantId) return;
    setSaving(true);
    setError(null);
    try {
      if (modalOpen === "add") {
        await api.post("/products", {
          name: formName.trim(),
          category: formCategory.trim(),
          description: formDescription.trim() || null,
        });
      } else if (editingProduct) {
        await api.patch(`/products/${editingProduct.id}`, {
          name: formName.trim(),
          category: formCategory.trim(),
          description: formDescription.trim() || null,
        });
      }
      setModalOpen(null);
      setEditingProduct(null);
      await loadProducts();
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存失败");
    } finally {
      setSaving(false);
    }
  }

  const filtered = products.filter(
    (p) =>
      !search.trim() ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <PageShell>
      <PageHeader
        icon={Package}
        title="我的产品库"
        description="管理产品信息，关联生成的笔记内容"
        actions={
          <Button onClick={openAdd}>
            <Plus className="h-4 w-4" />
            添加产品
          </Button>
        }
      />

      {error && (
        <div className="mb-4 rounded-2xl border border-red-200/80 bg-red-50 px-4 py-3 text-sm text-red-900 shadow-sm">
          {error}
        </div>
      )}

      <div className="relative mb-6">
        <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-stone-400" />
        <input
          type="text"
          placeholder="搜索产品名称或分类…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input-surface h-10 w-full max-w-md pl-10 pr-3 text-sm"
        />
      </div>

      {loading ? (
        <div className="flex min-h-[200px] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : filtered.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <Package className="h-12 w-12 text-stone-300" />
            <p className="mt-4 text-stone-600">
              {products.length === 0 ? "暂无产品，点击「添加产品」创建" : "没有匹配的产品"}
            </p>
            <Button variant="secondary" className="mt-4" onClick={openAdd}>
              <Plus className="h-4 w-4" />
              添加产品
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((product) => (
            <Card key={product.id} className="transition-shadow hover:shadow-md">
              <CardContent className="flex items-center gap-4 py-5">
                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-stone-100 to-stone-200">
                  <Package className="h-7 w-7 text-stone-400" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="truncate text-sm font-semibold text-stone-900">
                    {product.name}
                  </h3>
                  <p className="mt-0.5 text-xs text-stone-500">{product.category}</p>
                  {product.description && (
                    <p className="mt-1.5 line-clamp-2 text-xs text-stone-400">
                      {product.description}
                    </p>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => openEdit(product)}
                  className="shrink-0 rounded-lg p-2 text-stone-400 transition-colors hover:bg-stone-100 hover:text-stone-600"
                  title="编辑"
                >
                  <Pencil className="h-4 w-4" />
                </button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add/Edit modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-950/70 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl border border-stone-200/80 bg-white shadow-2xl shadow-stone-900/20">
            <div className="flex items-center justify-between border-b border-stone-200 px-5 py-4">
              <h2 className="text-lg font-semibold text-stone-900">
                {modalOpen === "add" ? "添加产品" : "编辑产品"}
              </h2>
              <button
                type="button"
                onClick={() => setModalOpen(null)}
                className="rounded p-1 text-stone-400 hover:bg-stone-100 hover:text-stone-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4 p-5">
              <Input
                label="产品名称"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="如：意睡眠经典床垫"
                required
              />
              <Input
                label="分类"
                value={formCategory}
                onChange={(e) => setFormCategory(e.target.value)}
                placeholder="如：床垫"
                required
              />
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-stone-700">描述（选填）</label>
                <textarea
                  value={formDescription}
                  onChange={(e) => setFormDescription(e.target.value)}
                  rows={3}
                  className="input-surface w-full rounded-xl px-3 py-2 text-sm"
                  placeholder="产品卖点、适用人群等"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="outline" onClick={() => setModalOpen(null)}>
                  取消
                </Button>
                <Button type="submit" disabled={saving || !formName.trim() || !formCategory.trim()}>
                  {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                  {saving ? "保存中…" : "保存"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </PageShell>
  );
}
