# XiaoHongShu AI Ads Workspace — Product Requirements Document

**产品名称：** 小红书AI广告工作台 (GenPos)
**版本：** v1.0
**状态：** Draft
**日期：** 2026-03-12

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Target Users](#2-target-users)
3. [Core Use Cases](#3-core-use-cases)
4. [Product Modes](#4-product-modes)
5. [Core Output Object — XiaoHongShu Note Package](#5-core-output-object--xiaohongshu-note-package)
6. [User Experience and Interface Design](#6-user-experience-and-interface-design)
7. [Creative Strategy](#7-creative-strategy)
8. [AI Agent Architecture](#8-ai-agent-architecture)
9. [Non-Goals for v1](#9-non-goals-for-v1)
10. [Success Metrics](#10-success-metrics)
11. [Compliance Requirements](#11-compliance-requirements)

---

## 1. Product Overview

GenPos (小红书AI广告工作台) is a **China-first, XiaoHongShu-first AI creative operating system** built for entrepreneurs and merchants. It continuously produces XiaoHongShu-native marketing content — notes, cover images, carousel assets, hashtag strategies, and paid-promotion packages — and lets founders interact with AI agents to generate urgent content on demand.

### Core Design Principles

| Principle | Description |
|---|---|
| **XiaoHongShu-native** | Every output is designed for XiaoHongShu's content graph, ranking signals, and audience behavior — not adapted from generic ad templates. |
| **Daily cadence** | The system auto-generates a daily slate of note packages per product per merchant, ensuring continuous presence without manual effort. |
| **On-demand responsiveness** | Entrepreneurs can request custom content at any time through natural-language chat or structured campaign forms; the system responds within seconds. |
| **Quarterly asset refresh** | Product-asset packs (photos, cutouts, style guides) are refreshed on a quarterly cycle to keep visuals current and seasonally relevant. |
| **Cartoon-first, product-real** | Creative generation defaults to cartoon/illustration contexts while preserving photographic fidelity of the actual product — the product is never distorted. |
| **聚光-ready** | Every note package can be flagged and formatted for 聚光 (XiaoHongShu's paid promotion system) with correct aspect ratios, CTA placement, and compliance metadata. |
| **蒲公英-ready** | The system generates structured creator-collaboration briefs compatible with 蒲公英 (XiaoHongShu's creator marketplace), including talking points, visual requirements, and brand guardrails. |
| **Multi-tenant** | Each merchant operates in an isolated workspace with independent brand rules, product libraries, asset packs, and performance histories. |
| **Configurable AI agent team** | Merchants can configure persona slots (e.g., 文案专家, 视觉策划, 数据分析师) that shape the tone, style, and strategic lens of generated content. |

### What GenPos Produces

The atomic output unit is the **XiaoHongShu Note Package** (笔记包) — a self-contained bundle that includes cover image, carousel images, title variants, body variants, first-comment text, hashtags, CTA configuration, and metadata for paid distribution and creator collaboration.

---

## 2. Target Users

### Primary

| Persona | Description | Key Need |
|---|---|---|
| **创业者 / 商家** (Entrepreneurs / Merchants) | Founders running products on XiaoHongShu who lack dedicated content teams. | Continuous, high-quality XiaoHongShu presence without hiring a content team. |
| **小红书运营** (XiaoHongShu Operators) | Dedicated operators managing one or more merchant accounts. | Multiplied output volume with consistent brand voice; faster turnaround on campaigns. |

### Secondary

| Persona | Description | Key Need |
|---|---|---|
| **增长营销人员** (Growth Marketers) | Marketing professionals focused on paid acquisition and organic growth on XiaoHongShu. | 聚光-ready assets, A/B title variants, performance-driven iteration. |
| **小型代运营机构** (Small Agencies) | Agencies serving multiple merchants who need scalable content operations. | Multi-tenant workspace to manage several merchant brands from one interface. |

---

## 3. Core Use Cases

### UC-1: Generate Daily XiaoHongShu Note Drafts Automatically

The system produces a configurable number of note packages per product per day (default: 3). Each package varies across style, angle, and hook to maximize creative diversity. Merchants review the daily slate each morning and approve, edit, or reject.

### UC-2: Generate Custom Ad/Note Instantly on Request

An entrepreneur opens the chat interface or structured form and describes what they need: "帮我做一条针对25-30岁职场女性的防晒霜笔记，强调成分安全，风格轻松". The system returns a complete note package within 15 seconds.

### UC-3: Create Cartoon-First Visual Assets While Preserving Product Truth

The system generates illustrated/cartoon scene contexts (e.g., a hand-drawn café table, a watercolor beach scene) and composites the real product photo into the scene. The product itself is never AI-generated or stylistically altered — only the surrounding context is illustrated.

### UC-4: Generate 聚光-Ready Variants

For any note package, the system can produce 聚光-optimized variants: adjusted aspect ratios (3:4 for feed, 1:1 for search), prominent CTA overlays, compliance-checked copy, and bid-strategy suggestions based on historical performance data.

### UC-5: Generate 蒲公英 Creator Briefs

The system auto-generates structured briefs for creator collaborations on 蒲公英, including: product summary, target audience description, required talking points, visual direction, brand do's and don'ts, example titles, suggested hashtags, and compensation notes.

### UC-6: Manage Brand Rules and Asset Packs

Merchants upload and maintain: product photos, cutout PNGs, logo files, brand color palettes, tone-of-voice guidelines, banned words (禁用词), required selling points (必须卖点), and competitor references. These assets form the constraints that all AI generation respects.

### UC-7: Approve/Reject and Queue Content

A review queue presents generated note packages with one-tap approve/reject. Approved packages enter a publishing queue with scheduled dates. Rejected packages feed back into the learning loop with optional rejection-reason tags.

### UC-8: Learn from Performance Over Time

The system ingests XiaoHongShu note performance data (impressions, engagement, saves, follows, conversions) and uses it to re-rank creative strategies, adjust style weights, and surface insights like "carousel posts with cartoon covers outperform photo covers by 34% for this product."

---

## 4. Product Modes

### 4.1 Daily Auto Mode — 每日自动生成

| Attribute | Detail |
|---|---|
| **Trigger** | Cron-based; runs at a configurable time daily (default: 06:00 CST). |
| **Input** | Active products in the merchant's library + brand rules + quarterly asset pack + performance history. |
| **Output** | N note packages per product (configurable, default 3), placed into the review queue. |
| **Variation strategy** | Each package draws from a different combination of style family, hook type, angle, and visual treatment — see [Creative Strategy](#7-creative-strategy). |
| **Merchant action** | Review the daily slate in 今日推荐 tab; approve, edit, or reject. |

### 4.2 On-Demand Request Mode — 一键/对话生成

| Attribute | Detail |
|---|---|
| **Trigger** | Merchant initiates via chat message or quick-generate button. |
| **Input** | Free-text prompt or selection from quick templates (e.g., "节日促销", "新品上架", "用户好评"). |
| **Output** | 1–5 note packages returned in under 15 seconds. |
| **Interaction** | Conversational refinement — the merchant can say "换个标题", "再活泼一点", "加上价格" and the system iterates. |

### 4.3 Guided Campaign Mode — 引导式投放生成

A structured wizard for merchants who want full control over campaign parameters. Fields:

| Field | Chinese Label | Type | Required |
|---|---|---|---|
| Product | 产品 | Select from product library | Yes |
| Industry | 行业 | Select / free text | Yes |
| Target Audience | 目标人群 | Multi-select tags + free text | Yes |
| Target Scenario | 目标场景 | Multi-select tags + free text | Yes |
| Publishing Objective | 发布目的 | Enum: 种草 / 转化 / 品牌曝光 / 活动引流 | Yes |
| 聚光 Promotion | 是否投聚光 | Boolean | Yes |
| 蒲公英 Collaboration | 是否做蒲公英合作 | Boolean | Yes |
| Visual Style | 风格 | Select from style families | No |
| Tone of Voice | 语气 | Select: 轻松 / 专业 / 种草感 / 闺蜜聊天 / 测评风 | No |
| Banned Words | 禁用词 | Text list | No |
| Required Selling Points | 必须出现的卖点 | Text list | Yes |
| Show Price | 是否带价格 | Boolean | No |
| CTA Type | CTA类型 | Enum: 点击链接 / 搜索关键词 / 私信咨询 / 到店体验 / 无CTA | Yes |

The wizard generates a full campaign batch (5–20 note packages) with all variants respecting the specified constraints.

---

## 5. Core Output Object — XiaoHongShu Note Package

The **note_package** is the atomic unit of output. Every generation mode produces one or more note_package objects.

### 5.1 JSON Schema

```json
{
  "note_package_id": "np_20260312_a1b2c3",
  "merchant_id": "m_001",
  "product_id": "p_sunscreen_001",
  "source_mode": "daily_auto | on_demand | guided_campaign",
  "objective": "种草 | 转化 | 品牌曝光 | 活动引流",
  "channel": "organic | 聚光 | 蒲公英",
  "persona": {
    "slot_id": "persona_copywriter",
    "name": "小美文案",
    "style_bias": "轻松种草"
  },
  "style_family": "watercolor | flat_vector | pixel_art | collage | minimal_line | pop_art",
  "quarter_asset_pack": "2026_Q1",
  "cover_asset": {
    "asset_id": "asset_cover_001",
    "url": "https://cdn.genpos.ai/covers/np_20260312_a1b2c3.jpg",
    "width": 1080,
    "height": 1440,
    "format": "jpg",
    "generation_method": "cartoon_composite"
  },
  "image_assets": [
    {
      "asset_id": "asset_img_001",
      "url": "https://cdn.genpos.ai/images/np_20260312_a1b2c3_01.jpg",
      "position": 1,
      "width": 1080,
      "height": 1440,
      "format": "jpg",
      "generation_method": "cartoon_composite | product_only | infographic"
    }
  ],
  "title_variants": [
    {
      "variant_id": "tv_01",
      "text": "这支防晒霜让我整个夏天都在线！☀️",
      "hook_type": "personal_story",
      "char_count": 18
    },
    {
      "variant_id": "tv_02",
      "text": "成分党狂喜！终于找到不闷痘的防晒",
      "hook_type": "ingredient_focus",
      "char_count": 17
    }
  ],
  "body_variants": [
    {
      "variant_id": "bv_01",
      "text": "姐妹们！！我真的要安利这支防晒霜...",
      "tone": "闺蜜聊天",
      "word_count": 280,
      "contains_price": false,
      "selling_points_covered": ["SPF50+", "不闷痘", "成膜快"]
    }
  ],
  "first_comment": {
    "text": "姐妹们有什么防晒问题可以问我～",
    "purpose": "engagement_hook"
  },
  "hashtags": [
    "#防晒霜推荐", "#夏日防晒", "#成分党", "#敏感肌防晒", "#好物分享"
  ],
  "cta_type": "搜索关键词 | 点击链接 | 私信咨询 | 到店体验 | 无CTA",
  "cta_value": "搜索「XX防晒霜」",
  "paid_ready": {
    "is_ready": true,
    "聚光_format_compliant": true,
    "aspect_ratios_generated": ["3:4", "1:1"],
    "estimated_bid_range": {
      "cpc_min": 0.5,
      "cpc_max": 2.0,
      "currency": "CNY"
    }
  },
  "creator_brief_ready": {
    "is_ready": true,
    "brief_text": "...",
    "target_creator_tags": ["美妆博主", "成分党", "护肤"],
    "collaboration_type": "图文笔记",
    "budget_range": {
      "min": 500,
      "max": 3000,
      "currency": "CNY"
    }
  },
  "compliance_status": {
    "layer_1_deterministic": "pass | fail",
    "layer_2_model_classifier": "pass | review | fail",
    "layer_3_human_review": "pending | approved | rejected",
    "overall": "pending | approved | rejected",
    "flags": []
  },
  "ranking_score": {
    "predicted_engagement": 0.73,
    "style_diversity_score": 0.85,
    "brand_alignment_score": 0.92,
    "composite_score": 0.82
  },
  "created_at": "2026-03-12T06:00:00+08:00",
  "updated_at": "2026-03-12T06:00:00+08:00",
  "status": "draft | pending_review | approved | rejected | published | archived"
}
```

### 5.2 Schema Field Reference

| Field | Type | Description |
|---|---|---|
| `note_package_id` | string | Globally unique identifier. Format: `np_{date}_{hash}`. |
| `merchant_id` | string | Tenant identifier. All queries are scoped to this. |
| `product_id` | string | Reference to the product in the merchant's product library. |
| `source_mode` | enum | Which generation mode produced this package. |
| `objective` | enum | The marketing objective this note serves. |
| `channel` | enum | Distribution channel: organic, 聚光 (paid), or 蒲公英 (creator). |
| `persona` | object | The AI persona slot that generated this content. |
| `style_family` | enum | The cartoon/illustration style family used for visuals. |
| `quarter_asset_pack` | string | Which quarterly asset pack was used. |
| `cover_asset` | object | The cover image metadata and CDN URL. |
| `image_assets` | array | Carousel image metadata; ordered by position. |
| `title_variants` | array | 2+ title options with hook-type annotation. |
| `body_variants` | array | 1+ body text options with tone and selling-point coverage. |
| `first_comment` | object | Suggested first comment for engagement seeding. |
| `hashtags` | array | Recommended hashtags, ordered by relevance. |
| `cta_type` | enum | Call-to-action type. |
| `cta_value` | string | The actual CTA text or link. |
| `paid_ready` | object | 聚光 readiness metadata. |
| `creator_brief_ready` | object | 蒲公英 brief readiness metadata. |
| `compliance_status` | object | Three-layer compliance check results. |
| `ranking_score` | object | Multi-signal ranking score for prioritization. |
| `status` | enum | Lifecycle status of the note package. |

---

## 6. User Experience and Interface Design

The workspace is organized into **10 primary tabs** accessible from a left-hand navigation rail. The interface language is Simplified Chinese with English-fallback for technical terms.

### 6.1 Tab Architecture

| Tab | Chinese Label | Purpose |
|---|---|---|
| **Today's Picks** | 今日推荐 | The merchant's daily content dashboard. Displays auto-generated note packages for the day, ranked by predicted performance. One-tap approve/reject. Visual card layout with cover preview, title, and key metrics. |
| **Quick Generate** | 一键生成 | Single-click generation interface. Merchant selects a product, optionally picks a quick template (节日促销, 新品上架, 用户好评, etc.), and taps generate. Results appear in under 15 seconds. |
| **AI Chat** | AI对话 | Free-form conversational interface to the AI agent team. Merchants describe what they need in natural language. Supports iterative refinement, follow-up requests, and multi-turn context. |
| **Product Library** | 我的产品库 | CRUD interface for managing products: upload photos, set selling points, define target audiences, attach pricing, link competitor references. Each product has a detail page with its generation history. |
| **Content Factory** | 内容工厂 | Bulk operations view. Campaign batch generation (Guided Campaign Mode), template management, asset pack configuration, and quarterly refresh scheduling. |
| **Review Queue** | 待审核 | Kanban-style board: Pending → Approved → Scheduled → Published. Drag-and-drop scheduling. Inline editing for titles, body text, and hashtags. Side-by-side comparison of variants. |
| **Distribution Center** | 投放中心 | 聚光 integration dashboard. View active promotions, monitor spend, see performance metrics (CPM, CPC, CTR, ROI). One-click creation of 聚光 ad units from approved note packages. |
| **Creator Collaboration** | 达人合作 | 蒲公英 integration hub. Browse and match creators, send briefs generated from note packages, track collaboration status, review creator drafts. |
| **Performance Analytics** | 成效分析 | Performance analytics across all published content. Engagement trends, top-performing styles, audience demographics, conversion funnels. Feeds data back into the ranking and generation algorithms. |
| **Brand Rules** | 品牌规则 | Configuration center for brand identity: tone of voice, visual guidelines, banned words (禁用词), required selling points, logo usage rules, color palettes, and competitive positioning notes. |

### 6.2 Interaction Patterns

- **Card-based browsing**: Note packages are presented as visual cards with cover image, title preview, predicted engagement score, and action buttons.
- **Inline editing**: Merchants can tap any text field (title, body, hashtags) to edit directly without opening a separate editor.
- **Side-by-side variants**: When multiple title or body variants exist, they appear side-by-side for easy comparison and selection.
- **Drag-and-drop scheduling**: Approved content can be dragged onto a calendar view to set publication dates.
- **Real-time generation**: On-demand and chat-based generation shows a streaming progress indicator; partial results appear as they're generated.

---

## 7. Creative Strategy

### 7.1 Visual Rule: Keep the Product Real. Cartoon the Context.

This is the foundational creative principle of GenPos:

> **The product photograph is sacred.** The AI never re-generates, stylizes, or alters the product itself. Instead, it generates illustrated, cartoon, or artistic *contexts* — backgrounds, scenes, decorative elements, hand-drawn annotations — and composites the real product into them.

**Why:** XiaoHongShu users trust authenticity. A stylized product image erodes trust and triggers "广告感" (ad-feeling) aversion. But a real product placed in a creative, eye-catching illustrated context *increases* stopping power while maintaining credibility.

### 7.2 Cartoon Style Families

Each style family defines a visual language for the context/background generation:

| Style Family | Description | Best For |
|---|---|---|
| **Watercolor** (水彩风) | Soft, hand-painted watercolor backgrounds. Organic, warm, slightly textured. | Beauty, skincare, food, wellness. |
| **Flat Vector** (扁平矢量) | Clean, modern vector illustrations. Bold colors, geometric shapes. | Tech, lifestyle gadgets, home goods. |
| **Pixel Art** (像素风) | Retro pixel-art scenes. Nostalgic, playful. | Snacks, beverages, youth-oriented products. |
| **Collage** (拼贴风) | Magazine-style collage with cutout elements, stickers, tape marks. | Fashion, accessories, multi-product showcases. |
| **Minimal Line** (极简线条) | Sparse line drawings with lots of white space. Elegant, upscale. | Premium skincare, luxury goods, minimalist brands. |
| **Pop Art** (波普风) | Bold outlines, halftone dots, saturated colors. High energy. | Sales events, limited editions, youth marketing. |

### 7.3 Daily Variation Strategy

To maximize creative diversity and A/B testing surface, the system generates variations across four independent axes:

| Axis | Possible Values | Count |
|---|---|---|
| **Style Family** | 6 styles | 6 |
| **Hook Type** | Personal story, ingredient/feature focus, problem-solution, social proof, listicle, question hook | 6 |
| **Visual Composition** | Product-centered, lifestyle scene, flat lay, before/after, infographic | 5 |
| **Tone** | 闺蜜聊天, 专业测评, 种草安利, 干货分享 | 4 |

**Total theoretical combinations per product:** 6 × 6 × 5 × 4 = **720**

The daily auto-generation system samples **24 candidate combinations** per product per day, generates note packages for each, scores them using the ranking model, and surfaces the top N (configurable, default 3) to the merchant's 今日推荐 queue. The remaining candidates are available in the 内容工厂 tab for manual browsing.

The sampling strategy uses:
- **Exploration (30%):** Random sampling across under-represented combinations.
- **Exploitation (70%):** Weighted sampling toward historically high-performing combinations for this product and audience.

This balance ensures creative freshness while optimizing for engagement.

---

## 8. AI Agent Architecture

### 8.1 Configurable Persona Slots

Each merchant workspace supports a configurable team of AI agent personas. Personas influence the stylistic and strategic lens of content generation.

| Default Persona | Role | Influence |
|---|---|---|
| **小美文案** (Copywriter) | Writes titles, body text, first comments. | Tone, vocabulary, hook strategy. |
| **设计喵** (Visual Planner) | Plans cover composition, selects style family, directs layout. | Visual style, image composition, color mood. |
| **数据达人** (Data Analyst) | Analyzes performance, adjusts ranking weights, surfaces insights. | Ranking model tuning, A/B test interpretation. |
| **合规卫士** (Compliance Guard) | Reviews all outputs against regulatory and platform rules. | Banned words, claim verification, ad disclosure. |

Merchants can:
- Rename personas to match their brand voice.
- Adjust persona style biases (e.g., make the copywriter more "专业" vs. "轻松").
- Add custom personas for specialized roles.
- Enable/disable personas per generation request.

### 8.2 Agent Orchestration

Generation requests are processed through an orchestration pipeline:

1. **Brief Assembly** — Collect inputs (product data, brand rules, campaign parameters, performance history).
2. **Visual Planning** — 设计喵 determines style family, composition, and asset requirements.
3. **Copy Generation** — 小美文案 produces title variants, body variants, first comment, and hashtags.
4. **Compliance Check** — 合规卫士 runs three-layer compliance (see [Section 11](#11-compliance-requirements)).
5. **Ranking** — 数据达人 scores packages and orders them by predicted performance.
6. **Packaging** — Assemble final note_package objects with all metadata.

---

## 9. Non-Goals for v1

The following are explicitly **out of scope** for the initial release:

| Non-Goal | Rationale |
|---|---|
| **Fully autonomous publishing for every merchant** | v1 requires human review before publishing. Auto-publish may be enabled per-merchant after trust is established, but is not a default. |
| **Full multi-country platform coverage** | v1 is XiaoHongShu-only. Douyin, WeChat Channels, Weibo, and international platforms (Instagram, TikTok) are deferred to v2+. |
| **Fully autonomous budget optimization** | v1 provides bid-range suggestions for 聚光 but does not auto-adjust budgets. Full programmatic optimization requires deeper 聚光 API integration and merchant trust-building. |
| **Long-form video-first generation** | v1 focuses on static images and carousel content. Short-form video (< 60s) may be explored as a v1.5 extension, but video is not the primary output format. |
| **Real-time XiaoHongShu API publishing** | v1 generates content packages for manual posting or scheduled queue. Direct API publishing depends on XiaoHongShu partner API access. |
| **Custom model fine-tuning per merchant** | v1 uses prompt engineering and retrieval-augmented generation. Per-merchant fine-tuned models are a v2 consideration. |

---

## 10. Success Metrics

### 10.1 Product Health Metrics

| Metric | Definition | v1 Target |
|---|---|---|
| **Daily Active Merchants** | Unique merchants who interact with the workspace daily. | 500 within 90 days of launch. |
| **Note Packages Generated / Day** | Total note packages generated across all merchants. | 10,000 / day within 90 days. |
| **Approval Rate** | % of auto-generated packages approved by merchants (with or without edits). | ≥ 60% |
| **Time to First Package** | Time from merchant sign-up to first note package generated. | < 10 minutes. |
| **Generation Latency (p95)** | Time from request to complete note package delivery. | < 15 seconds for on-demand; < 5 minutes for daily batch per merchant. |

### 10.2 Content Quality Metrics

| Metric | Definition | v1 Target |
|---|---|---|
| **Average Engagement Rate** | (Likes + Saves + Comments) / Impressions for published GenPos content. | ≥ XiaoHongShu category median. |
| **Edit Rate** | % of approved packages that were edited before publishing. | ≤ 40% (declining over time as the system learns). |
| **Compliance Pass Rate** | % of packages that pass all three compliance layers on first generation. | ≥ 90% |
| **Performance Lift** | Engagement of GenPos content vs. merchant's pre-GenPos baseline. | ≥ 20% lift within 60 days. |

### 10.3 Business Metrics

| Metric | Definition | v1 Target |
|---|---|---|
| **Merchant Retention (30-day)** | % of merchants active 30 days after onboarding. | ≥ 70% |
| **聚光 Activation Rate** | % of merchants who create at least one 聚光 campaign from GenPos. | ≥ 25% |
| **蒲公英 Brief Sent Rate** | % of merchants who send at least one 蒲公英 brief from GenPos. | ≥ 15% |
| **Revenue per Merchant (Monthly)** | Average monthly revenue per active merchant. | Defined post-pricing finalization. |

---

## 11. Compliance Requirements

XiaoHongShu content must comply with platform rules, PRC advertising law (《广告法》), and industry-specific regulations. GenPos implements a **three-layer compliance system** that processes every note package before it enters the review queue.

### 11.1 Layer 1 — Deterministic Rules Engine

A rule-based system that catches clear-cut violations with zero ambiguity.

| Rule Category | Examples |
|---|---|
| **Absolute banned words** | 最, 第一, 国家级, 顶级, 极品, and other superlatives prohibited by 《广告法》Article 9. |
| **Industry-specific banned claims** | Medical efficacy claims for cosmetics, guaranteed returns for financial products, unapproved health claims for food. |
| **Platform formatting rules** | Title length limits, banned emoji combinations, prohibited link formats. |
| **Merchant-specific banned words** | Custom 禁用词 lists defined in the merchant's brand rules. |
| **Required disclosures** | Ad disclosure tags (广告, 合作) when required for 聚光 or 蒲公英 content. |

**Behavior:** Deterministic pass/fail. Failed packages are flagged with specific rule IDs and blocked from the review queue until the violating content is corrected (auto-corrected or manually fixed).

### 11.2 Layer 2 — Model-Based Classifiers

ML/LLM-based classifiers that catch nuanced or context-dependent violations.

| Classifier | Purpose |
|---|---|
| **Implied superlative detector** | Catches phrases that imply "best" without using the literal banned word (e.g., "没有比这更好的了"). |
| **Misleading claim detector** | Identifies claims that are technically legal but misleading in context. |
| **Sensitive content classifier** | Flags content touching politically sensitive, sexually suggestive, or violence-adjacent themes. |
| **Competitive disparagement detector** | Catches implicit or explicit negative comparisons to competitors. |
| **Tone appropriateness scorer** | Ensures content tone matches platform norms and doesn't feel overly aggressive or salesy. |

**Behavior:** Three-state output: pass, review (requires human attention), fail. Review-flagged packages are routed to the merchant's review queue with classifier explanations.

### 11.3 Layer 3 — Human Review

Human-in-the-loop review for packages that pass Layers 1–2 but require final judgment.

| Scenario | Action |
|---|---|
| **Standard auto-generated content** | Merchant reviews in 待审核 tab. One-tap approve or reject. |
| **Layer 2 review-flagged content** | Highlighted with classifier reasons. Merchant decides. |
| **聚光 paid content** | Mandatory merchant approval before 聚光 submission. |
| **蒲公英 creator briefs** | Mandatory merchant approval before brief delivery. |
| **New merchant (first 30 days)** | All content routed through review — no auto-approve. |

### 11.4 Compliance Feedback Loop

Rejected content (by any layer) feeds back into the system:
- Deterministic rules are updated when new platform policy changes are announced.
- Model classifiers are retrained quarterly on accumulated rejection data.
- Per-merchant patterns are learned (e.g., "this merchant always rejects content with price mentions" → suppress price in future generations).

---

## Appendix A: Glossary

| Term | Definition |
|---|---|
| **笔记包 (Note Package)** | The core output object — a complete XiaoHongShu note with all assets and metadata. |
| **聚光** | XiaoHongShu's paid promotion platform for merchants. |
| **蒲公英** | XiaoHongShu's creator collaboration marketplace. |
| **禁用词** | Banned words — terms that must not appear in any generated content. |
| **种草** | "Planting grass" — XiaoHongShu slang for creating desire/interest in a product. |
| **CTA** | Call to Action — the desired user behavior after viewing the note. |
| **Asset Pack** | A quarterly-refreshed bundle of product photos, cutouts, and brand assets. |
| **Style Family** | A visual language (watercolor, flat vector, etc.) applied to context generation. |

---

## Appendix B: Open Questions

| # | Question | Owner | Status |
|---|---|---|---|
| 1 | XiaoHongShu Partner API access timeline and scope? | BD | Open |
| 2 | 聚光 API integration depth — can we auto-create ad units or only export? | Engineering | Open |
| 3 | 蒲公英 API availability for brief delivery? | BD | Open |
| 4 | Pricing model: per-merchant subscription vs. per-note-package usage? | Product/Finance | Open |
| 5 | On-device vs. cloud-only generation for latency-sensitive merchants? | Engineering | Open |
| 6 | Data residency requirements for PRC compliance (data localization)? | Legal/Infra | Open |
