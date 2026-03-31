"use client";

import { useEffect, useState } from "react";
import { Shield, Loader2 } from "lucide-react";
import { PageHeader, PageShell } from "@/components/layout/page-shell";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { ensureAuth, getMerchantId } from "@/lib/auth";

interface Merchant {
  id: string;
  name: string;
  industry: string;
  xhs_account_type: string;
  uses_juguang: boolean;
  uses_pugongying: boolean;
  language: string;
  timezone: string;
}

interface MerchantRules {
  tone_preset: string | null;
  banned_words: string[];
  required_claims: string[];
  banned_claims: string[];
  compliance_level: string;
  review_mode: string;
}

const XHS_ACCOUNT_OPTIONS = [
  { value: "personal", label: "个人号" },
  { value: "professional", label: "专业号" },
  { value: "enterprise", label: "企业号" },
];

const COMPLIANCE_OPTIONS = [
  { value: "strict", label: "严格" },
  { value: "standard", label: "标准" },
  { value: "relaxed", label: "宽松" },
];

const REVIEW_MODE_OPTIONS = [
  { value: "all", label: "全部人工审核" },
  { value: "sampling", label: "抽样审核" },
  { value: "auto", label: "达标自动通过" },
];

function arrFromUnknown(v: unknown): string[] {
  if (Array.isArray(v)) return v.filter((x) => typeof x === "string");
  if (typeof v === "object" && v && "words" in (v as object))
    return (v as { words: string[] }).words || [];
  return [];
}

export default function RulesPage() {
  const [merchant, setMerchant] = useState<Merchant | null>(null);
  const [rules, setRules] = useState<MerchantRules | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [xhsAccountType, setXhsAccountType] = useState("professional");
  const [usesJuguang, setUsesJuguang] = useState(false);
  const [usesPugongying, setUsesPugongying] = useState(false);
  const [tonePreset, setTonePreset] = useState("");
  const [complianceLevel, setComplianceLevel] = useState("standard");
  const [reviewMode, setReviewMode] = useState("all");
  const [bannedWordsStr, setBannedWordsStr] = useState("");
  const [requiredClaimsStr, setRequiredClaimsStr] = useState("");
  const [bannedClaimsStr, setBannedClaimsStr] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        await ensureAuth();
        const mid = getMerchantId();
        if (!mid) return;
        const [m, r] = await Promise.all([
          api.get<Merchant>(`/merchants/${mid}`),
          api.get<MerchantRules & { banned_words?: unknown }>(`/merchants/${mid}/rules`).catch(() => null),
        ]);
        if (cancelled) return;
        setMerchant(m);
        setName(m.name);
        setIndustry(m.industry);
        setXhsAccountType(m.xhs_account_type);
        setUsesJuguang(m.uses_juguang);
        setUsesPugongying(m.uses_pugongying);
        if (r) {
          setRules(r);
          setTonePreset(r.tone_preset || "");
          setComplianceLevel(r.compliance_level);
          setReviewMode(r.review_mode);
          setBannedWordsStr(arrFromUnknown(r.banned_words).join("\n"));
          setRequiredClaimsStr(arrFromUnknown(r.required_claims).join("\n"));
          setBannedClaimsStr(arrFromUnknown(r.banned_claims).join("\n"));
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "加载失败");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  async function handleSave() {
    const mid = getMerchantId();
    if (!mid) return;
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      await api.patch(`/merchants/${mid}`, {
        name,
        industry,
        xhs_account_type: xhsAccountType,
        uses_juguang: usesJuguang,
        uses_pugongying: usesPugongying,
      });
      await api.patch(`/merchants/${mid}/rules`, {
        tone_preset: tonePreset || null,
        compliance_level: complianceLevel,
        review_mode: reviewMode,
        banned_words: bannedWordsStr.trim() ? bannedWordsStr.trim().split(/\n/).map((s) => s.trim()).filter(Boolean) : [],
        required_claims: requiredClaimsStr.trim() ? requiredClaimsStr.trim().split(/\n/).map((s) => s.trim()).filter(Boolean) : [],
        banned_claims: bannedClaimsStr.trim() ? bannedClaimsStr.trim().split(/\n/).map((s) => s.trim()).filter(Boolean) : [],
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存失败");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <PageShell className="max-w-5xl">
        <div className="flex min-h-[40vh] items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </PageShell>
    );
  }

  if (error && !merchant) {
    return (
      <PageShell className="max-w-5xl">
        <div className="rounded-2xl border border-red-200/80 bg-red-50 p-8 text-sm text-red-900 shadow-sm">
          {error}
        </div>
      </PageShell>
    );
  }

  return (
    <PageShell className="max-w-5xl">
      <PageHeader
        icon={Shield}
        title="品牌规则"
        description="管理品牌信息与内容规范，AI 生成内容时将自动遵守"
        actions={
          <Button onClick={handleSave} disabled={saving}>
            {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            {saving ? "保存中…" : saved ? "已保存" : "保存"}
          </Button>
        }
      />

      {error && (
        <div className="mb-4 rounded-2xl border border-red-200/80 bg-red-50 px-4 py-3 text-sm text-red-900 shadow-sm">
          {error}
        </div>
      )}

      {/* 品牌信息 */}
      <Card className="mb-6">
        <CardHeader>
          <h2 className="text-lg font-semibold text-stone-900">品牌信息</h2>
          <p className="text-sm text-stone-500">基础信息与小红书账号设置</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              label="品牌名称"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="意睡眠 Easysleep"
            />
            <Input
              label="所属行业"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              placeholder="家居"
            />
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-stone-700">账号类型</label>
              <select
                value={xhsAccountType}
                onChange={(e) => setXhsAccountType(e.target.value)}
                className="input-surface h-10 w-full px-3 text-sm"
              >
                {XHS_ACCOUNT_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-wrap items-center gap-6 pt-2">
              <label className="flex items-center gap-2 text-sm text-stone-700">
                <input
                  type="checkbox"
                  checked={usesJuguang}
                  onChange={(e) => setUsesJuguang(e.target.checked)}
                  className="h-4 w-4 rounded border-stone-300 text-primary focus:ring-primary"
                />
                使用聚光投放
              </label>
              <label className="flex items-center gap-2 text-sm text-stone-700">
                <input
                  type="checkbox"
                  checked={usesPugongying}
                  onChange={(e) => setUsesPugongying(e.target.checked)}
                  className="h-4 w-4 rounded border-stone-300 text-primary focus:ring-primary"
                />
                使用蒲公英合作
              </label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 内容规则 */}
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold text-stone-900">内容规则</h2>
          <p className="text-sm text-stone-500">语调、合规等级与审核方式</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            label="语调预设"
            value={tonePreset}
            onChange={(e) => setTonePreset(e.target.value)}
            placeholder="温暖亲切、专业可信"
          />
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-stone-700">合规等级</label>
              <select
                value={complianceLevel}
                onChange={(e) => setComplianceLevel(e.target.value)}
                className="input-surface h-10 w-full px-3 text-sm"
              >
                {COMPLIANCE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-stone-700">审核模式</label>
              <select
                value={reviewMode}
                onChange={(e) => setReviewMode(e.target.value)}
                className="input-surface h-10 w-full px-3 text-sm"
              >
                {REVIEW_MODE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-stone-700">禁用词（每行一个）</label>
            <textarea
              value={bannedWordsStr}
              onChange={(e) => setBannedWordsStr(e.target.value)}
              rows={3}
              className="input-surface w-full rounded-xl px-3 py-2 text-sm placeholder:text-stone-400"
              placeholder="绝对化用语、未获批功效词等"
            />
          </div>
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-stone-700">必须包含的声明（每行一个）</label>
            <textarea
              value={requiredClaimsStr}
              onChange={(e) => setRequiredClaimsStr(e.target.value)}
              rows={2}
              className="input-surface w-full rounded-xl px-3 py-2 text-sm placeholder:text-stone-400"
              placeholder="例如：成分说明、使用说明"
            />
          </div>
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-stone-700">禁止使用的声明（每行一个）</label>
            <textarea
              value={bannedClaimsStr}
              onChange={(e) => setBannedClaimsStr(e.target.value)}
              rows={2}
              className="input-surface w-full rounded-xl px-3 py-2 text-sm placeholder:text-stone-400"
              placeholder="例如：医疗功效、绝对化承诺"
            />
          </div>
        </CardContent>
      </Card>
    </PageShell>
  );
}
