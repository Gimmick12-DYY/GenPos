# GenPos — Frontend Information Architecture

> **Version:** 0.1.0-draft
> **Last updated:** 2026-03-12
> **Status:** Living document — evolves with the system
> **Parent:** [PRD](prd/PRD.md) § 6 · [Architecture](architecture/ARCHITECTURE.md) § 3–5 · [Agent Team Spec](architecture/AGENT_TEAM_SPEC.md) § 10
> **Tech stack:** Next.js 14+ / TypeScript / Tailwind CSS / App Router

---

## Table of Contents

1. [Design Philosophy](#1-design-philosophy)
2. [Navigation Structure](#2-navigation-structure)
3. [Routing Map](#3-routing-map)
4. [Page Specifications](#4-page-specifications)
5. [Shared Component Architecture](#5-shared-component-architecture)
6. [Design System Notes](#6-design-system-notes)
7. [State Management](#7-state-management)
8. [Admin Pages — Agent Team Management](#8-admin-pages--agent-team-management)
9. [Layout Structure](#9-layout-structure)
10. [Responsive Behavior](#10-responsive-behavior)

---

## 1. Design Philosophy

| Principle | Description |
|---|---|
| **Chinese-first** | All labels, navigation, and default content are Simplified Chinese. English is used only for technical terms where no standard Chinese equivalent exists (`CTA`, `URL`). |
| **Desktop-first, mobile-responsive** | The primary use case is a desktop workspace. Mobile views degrade gracefully — complex tables collapse to cards, sidebars become drawers. |
| **Card-based content browsing** | Note packages are always presented as visual cards with cover image, title preview, ranking score, and action buttons. This mirrors how content appears on XiaoHongShu itself. |
| **Clean and spacious** | Generous whitespace, restrained color usage, and clear visual hierarchy. This is a professional workspace, not a social feed — avoid visual clutter. |
| **XiaoHongShu-native preview** | All note previews must render at XiaoHongShu-accurate aspect ratios (3:4 for feed, 1:1 for search) so merchants see exactly what their audience will see. |
| **Warm professionalism** | The color palette and typography evoke warmth and creativity without sacrificing trustworthiness. The product is for entrepreneurs who are building brands — the tool should feel empowering. |

---

## 2. Navigation Structure

The application uses a **persistent left-hand navigation rail** with 10 primary tabs, grouped by function. The rail is always visible on desktop and collapses to an icon-only rail or bottom bar on mobile.

### 2.1 Primary Navigation Tabs

| # | Chinese Label | English Label | Icon | Route | Purpose |
|---|---|---|---|---|---|
| 1 | **今日推荐** | Today's Recommendations | `☀️` Sparkle / Calendar | `/dashboard` | Daily auto-generated content — the merchant's morning inbox. |
| 2 | **一键生成** | One-Click Generate | `⚡` Lightning / Wand | `/generate` | Structured generation form for Guided Campaign Mode. |
| 3 | **AI对话** | AI Chat | `💬` Chat Bubble | `/chat` | Conversational content generation with the Founder Copilot agent. |
| 4 | **我的产品库** | My Products | `📦` Package / Box | `/products` | Product catalog, asset packs, and brand asset management. |
| 5 | **内容工厂** | Content Factory | `🏭` Factory / Grid | `/factory` | Comprehensive list of all generated note packages. |
| 6 | **待审核** | Pending Review | `✅` Checkmark / Shield | `/review` | Approval workflow and compliance review queue. |
| 7 | **投放中心** | Distribution Center | `🚀` Rocket / Send | `/distribution` | Export management for 笔记, 聚光, and 蒲公英. |
| 8 | **达人合作** | Creator Collaboration | `🤝` Handshake / Star | `/creators` | 蒲公英-ready brief management and creator matching. |
| 9 | **成效分析** | Performance Analytics | `📊` Chart / Trend | `/analytics` | Performance dashboards and content insights. |
| 10 | **品牌规则** | Brand Rules | `⚙️` Gear / Shield | `/rules` | Tone presets, banned words, compliance configuration. |

### 2.2 Navigation Grouping

The rail visually groups tabs with subtle dividers:

```
┌──────────────────────────┐
│  GenPos Logo             │
├──────────────────────────┤
│  📝 CONTENT              │
│  ├─ 今日推荐             │
│  ├─ 一键生成             │
│  └─ AI对话               │
├──────────────────────────┤
│  📦 ASSETS               │
│  └─ 我的产品库           │
├──────────────────────────┤
│  🔄 OPERATIONS           │
│  ├─ 内容工厂             │
│  ├─ 待审核               │
│  └─ 投放中心             │
├──────────────────────────┤
│  📈 INTELLIGENCE         │
│  ├─ 达人合作             │
│  ├─ 成效分析             │
│  └─ 品牌规则             │
├──────────────────────────┤
│  👤 Account / Settings   │
│  ⚙️ Admin (if admin role)│
└──────────────────────────┘
```

### 2.3 Secondary Navigation

| Location | Label | Route | Visibility |
|---|---|---|---|
| Account menu (bottom of rail) | 账号设置 (Account Settings) | `/settings` | All users |
| Account menu | 团队管理 (Team Management) | `/settings/team` | Owner / Admin |
| Admin section | Agent团队设计 (Agent Team Designer) | `/admin/teams` | Admin role only |
| Admin section | 人设库 (Persona Library) | `/admin/personas` | Admin role only |
| Admin section | 实验面板 (Experiment Dashboard) | `/admin/experiments` | Admin role only |

---

## 3. Routing Map

All routes use the Next.js App Router (`app/` directory). Routes are tenant-scoped via the JWT — no tenant prefix in the URL path.

### 3.1 Complete Route Table

| Route | Page Title (Chinese) | Description |
|---|---|---|
| `/` | — | Redirect to `/dashboard` |
| `/dashboard` | 今日推荐 | Today's recommended note packages |
| `/generate` | 一键生成 | Guided Campaign generation form |
| `/chat` | AI对话 | Conversational AI interface |
| `/chat/:conversationId` | AI对话 | Specific conversation thread |
| `/products` | 我的产品库 | Product list |
| `/products/:id` | 产品详情 | Product detail page |
| `/products/:id/assets` | 素材管理 | Asset pack management for a product |
| `/factory` | 内容工厂 | All note packages |
| `/factory/:id` | 笔记包详情 | Note package detail view |
| `/review` | 待审核 | Review queue |
| `/review/:id` | 审核详情 | Single note package review with compliance panel |
| `/distribution` | 投放中心 | Export management |
| `/distribution/exports/:id` | 导出详情 | Export bundle detail |
| `/creators` | 达人合作 | Creator brief management |
| `/creators/briefs/:id` | 简报详情 | Brief detail |
| `/analytics` | 成效分析 | Performance analytics dashboard |
| `/analytics/products/:id` | 产品成效 | Product-level performance drill-down |
| `/analytics/notes/:id` | 内容成效 | Note-level performance drill-down |
| `/rules` | 品牌规则 | Brand rules and compliance settings |
| `/settings` | 账号设置 | Account settings |
| `/settings/team` | 团队管理 | Team member management |
| `/admin/teams` | Agent团队设计 | Agent Team Designer (admin) |
| `/admin/teams/:id` | 团队详情 | Specific team composition view |
| `/admin/personas` | 人设库 | Persona Library (admin) |
| `/admin/personas/:id` | 人设详情 | Persona detail and editor |
| `/admin/experiments` | 实验面板 | Persona A/B test dashboard (admin) |
| `/admin/experiments/:id` | 实验详情 | Experiment detail (admin) |
| `/login` | 登录 | Login page (unauthenticated layout) |
| `/onboarding` | 新手引导 | Post-signup onboarding wizard |

### 3.2 App Router Directory Structure

```
apps/web/app/
├── layout.tsx                     # Root layout: auth check, providers, navigation shell
├── page.tsx                       # Redirect to /dashboard
├── globals.css
│
├── (auth)/                        # Unauthenticated layout group
│   ├── layout.tsx
│   ├── login/page.tsx
│   └── onboarding/page.tsx
│
├── (workspace)/                   # Authenticated layout group (main shell + nav rail)
│   ├── layout.tsx                 # Navigation rail + content area
│   ├── dashboard/
│   │   └── page.tsx               # 今日推荐
│   ├── generate/
│   │   └── page.tsx               # 一键生成
│   ├── chat/
│   │   ├── page.tsx               # AI对话 (new conversation)
│   │   └── [conversationId]/
│   │       └── page.tsx           # Specific conversation
│   ├── products/
│   │   ├── page.tsx               # 我的产品库
│   │   └── [id]/
│   │       ├── page.tsx           # 产品详情
│   │       └── assets/
│   │           └── page.tsx       # 素材管理
│   ├── factory/
│   │   ├── page.tsx               # 内容工厂
│   │   └── [id]/
│   │       └── page.tsx           # 笔记包详情
│   ├── review/
│   │   ├── page.tsx               # 待审核
│   │   └── [id]/
│   │       └── page.tsx           # 审核详情
│   ├── distribution/
│   │   ├── page.tsx               # 投放中心
│   │   └── exports/
│   │       └── [id]/
│   │           └── page.tsx       # 导出详情
│   ├── creators/
│   │   ├── page.tsx               # 达人合作
│   │   └── briefs/
│   │       └── [id]/
│   │           └── page.tsx       # 简报详情
│   ├── analytics/
│   │   ├── page.tsx               # 成效分析
│   │   ├── products/
│   │   │   └── [id]/
│   │   │       └── page.tsx       # 产品成效
│   │   └── notes/
│   │       └── [id]/
│   │           └── page.tsx       # 内容成效
│   ├── rules/
│   │   └── page.tsx               # 品牌规则
│   └── settings/
│       ├── page.tsx               # 账号设置
│       └── team/
│           └── page.tsx           # 团队管理
│
└── (admin)/                       # Admin layout group (admin-only nav)
    ├── layout.tsx                 # Admin role guard + admin nav
    └── admin/
        ├── teams/
        │   ├── page.tsx           # Agent团队设计
        │   └── [id]/
        │       └── page.tsx       # 团队详情
        ├── personas/
        │   ├── page.tsx           # 人设库
        │   └── [id]/
        │       └── page.tsx       # 人设详情
        └── experiments/
            ├── page.tsx           # 实验面板
            └── [id]/
                └── page.tsx       # 实验详情
```

---

## 4. Page Specifications

### 4.1 今日推荐 — Today's Recommendations (`/dashboard`)

The merchant's daily content inbox. This is the landing page after login — optimized for fast review-and-approve of auto-generated content.

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│  Header: "今日推荐" + Date (2026年3月12日) + Unreviewed Count│
├──────────────────────────────────────────────────────────────┤
│  Hero Section                                                │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  🏆 Today's Top Pick — highest ranking score         │     │
│  │  [Large cover image]  [Title + Body preview]         │     │
│  │  [Score: 0.92]  [Style: 水彩风]  [✅ Compliant]     │     │
│  │  [Approve] [Edit] [Reject] [Export]                  │     │
│  └─────────────────────────────────────────────────────┘     │
├──────────────────────────────────────────────────────────────┤
│  Filter Bar                                                  │
│  [Product ▾] [Objective ▾] [Style ▾] [Persona ▾]           │
│  Sort: [Ranking Score ▾] [Created ▾]                        │
├──────────────────────────────────────────────────────────────┤
│  Card Grid (3-4 columns)                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Cover    │ │ Cover    │ │ Cover    │ │ Cover    │       │
│  │ Image    │ │ Image    │ │ Image    │ │ Image    │       │
│  │ (3:4)    │ │ (3:4)    │ │ (3:4)    │ │ (3:4)    │       │
│  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤       │
│  │ Title    │ │ Title    │ │ Title    │ │ Title    │       │
│  │ Score 87 │ │ Score 83 │ │ Score 79 │ │ Score 76 │       │
│  │ 水彩风   │ │ 扁平矢量 │ │ 拼贴风   │ │ 极简线条 │       │
│  │ ✅ Pass  │ │ ⚠️ Review│ │ ✅ Pass  │ │ ✅ Pass  │       │
│  │ [✓][✗][→]│ │ [✓][✗][→]│ │ [✓][✗][→]│ │ [✓][✗][→]│       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ... (paginated or infinite scroll)                          │
└──────────────────────────────────────────────────────────────┘
```

**Data requirements:**
- `GET /api/v1/note-packages?status=pending_review&source_mode=daily_auto&sort=-ranking_score`
- Each card: `note_package_id`, `cover_asset.url`, `title_variants[0].text`, `ranking_score.composite_score`, `style_family`, `compliance_status.overall`

**Interactions:**
- **Approve** → `PATCH /api/v1/note-packages/{id}/review` with `action: "approve"`
- **Reject** → opens rejection reason modal → `PATCH /api/v1/note-packages/{id}/review` with `action: "reject"` and `reason`
- **Edit** → navigates to `/factory/{id}` in edit mode
- **Export** → opens export channel selector modal
- **Card click** → expands to full note preview (modal or slide-out panel)

**Filters:**
| Filter | Source | Type |
|---|---|---|
| 产品 (Product) | `GET /api/v1/products` | Dropdown |
| 目标 (Objective) | Enum: 种草, 转化, 品牌曝光, 活动引流 | Multi-select |
| 风格 (Style Family) | Enum: 水彩风, 扁平矢量, 像素风, 拼贴风, 极简线条, 波普风 | Multi-select |
| 人设 (Persona) | `GET /api/v1/personas` | Dropdown |
| 合规状态 (Compliance) | Enum: pass, review, fail, pending | Multi-select |

---

### 4.2 一键生成 — One-Click Generate (`/generate`)

A structured form that maps directly to the `StructuredJobRequest` schema (see AGENT_TEAM_SPEC § 12.1). This is the Guided Campaign Mode from the PRD.

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│  Header: "一键生成" + subtitle "填写参数，一键生成笔记包"     │
├──────────────────────────────────────────────────────────────┤
│  Form (2-column layout on desktop)                           │
│                                                              │
│  LEFT COLUMN (Required Fields)                               │
│  ┌────────────────────────────────┐                          │
│  │ 产品 *                         │                          │
│  │ [Dropdown: select from library]│                          │
│  ├────────────────────────────────┤                          │
│  │ 行业 *                         │                          │
│  │ [Auto-filled from profile]     │                          │
│  ├────────────────────────────────┤                          │
│  │ 目标人群 *                     │                          │
│  │ [Tag input with suggestions]   │                          │
│  │ e.g. 都市白领, 学生党, 宝妈    │                          │
│  ├────────────────────────────────┤                          │
│  │ 目标场景 *                     │                          │
│  │ [Dropdown: 通勤/约会/旅行/...]  │                          │
│  ├────────────────────────────────┤                          │
│  │ 发布目的 *                     │                          │
│  │ (●) 种草  (○) 转化             │                          │
│  │ (○) 品牌曝光  (○) 活动引流     │                          │
│  ├────────────────────────────────┤                          │
│  │ 必须出现的卖点 *               │                          │
│  │ [Tag input: SPF50+ | 不闷痘]   │                          │
│  ├────────────────────────────────┤                          │
│  │ CTA类型 *                      │                          │
│  │ [Dropdown: 点击链接/搜索关键词/ │                          │
│  │  私信咨询/到店体验/无CTA]       │                          │
│  └────────────────────────────────┘                          │
│                                                              │
│  RIGHT COLUMN (Optional / Style Fields)                      │
│  ┌────────────────────────────────┐                          │
│  │ 是否投聚光                      │                          │
│  │ [Toggle: OFF]                  │                          │
│  ├────────────────────────────────┤                          │
│  │ 是否做蒲公英合作               │                          │
│  │ [Toggle: OFF]                  │                          │
│  ├────────────────────────────────┤                          │
│  │ 风格                           │                          │
│  │ ┌─────┐┌─────┐┌─────┐         │                          │
│  │ │水彩风││扁平 ││像素风│         │                          │
│  │ │[img]││矢量 ││[img]│         │                          │
│  │ │     ││[img]││     │         │                          │
│  │ └─────┘└─────┘└─────┘         │                          │
│  │ ┌─────┐┌─────┐┌─────┐         │                          │
│  │ │拼贴风││极简 ││波普风│         │                          │
│  │ │[img]││线条 ││[img]│         │                          │
│  │ │     ││[img]││     │         │                          │
│  │ └─────┘└─────┘└─────┘         │                          │
│  ├────────────────────────────────┤                          │
│  │ 语气                           │                          │
│  │ [闺蜜聊天][专业测评]           │                          │
│  │ [种草安利][干货分享]           │                          │
│  ├────────────────────────────────┤                          │
│  │ 禁用词                         │                          │
│  │ [Tag input: 最好 | 第一]        │                          │
│  ├────────────────────────────────┤                          │
│  │ 是否带价格                      │                          │
│  │ [Toggle: OFF]                  │                          │
│  ├────────────────────────────────┤                          │
│  │ 生成数量                        │                          │
│  │ [Slider: 1 ─── 5 ─── 10 ── 20]│                          │
│  └────────────────────────────────┘                          │
├──────────────────────────────────────────────────────────────┤
│  [🚀 开始生成] (Primary action button, full width)           │
├──────────────────────────────────────────────────────────────┤
│  Generation Results Area                                     │
│  (Hidden until generation completes)                         │
│  ┌─────────────────────────────────────────────────────┐     │
│  │  ⏳ Generating... 3/5 note packages ready            │     │
│  │  [Progress bar with streaming indicator]             │     │
│  └─────────────────────────────────────────────────────┘     │
│  ... then replaced by NotePackageCard grid ...               │
└──────────────────────────────────────────────────────────────┘
```

**Form → API mapping:**
| Form Field | Chinese Label | API Field (`StructuredJobRequest`) | Required |
|---|---|---|---|
| Product | 产品 | `product_ids` | Yes |
| Industry | 行业 | Auto from merchant profile | Yes |
| Target Audience | 目标人群 | `target_audience.tags` | Yes |
| Target Scenario | 目标场景 | `target_audience.scenarios` | Yes |
| Publishing Objective | 发布目的 | `objective` | Yes |
| Use Juguang | 是否投聚光 | `channels` (includes `"聚光"`) | Yes |
| Use Pugongying | 是否做蒲公英合作 | `channels` (includes `"蒲公英"`) | Yes |
| Style | 风格 | `style_preference` | No |
| Tone | 语气 | `tone_preference` | No |
| Banned Words | 禁用词 | `banned_words` | No |
| Required Selling Points | 必须出现的卖点 | `required_selling_points` | Yes |
| Include Price | 是否带价格 | `include_price` | No |
| CTA Type | CTA类型 | `cta_type` | Yes |
| Variant Count | 生成数量 | `variant_count` | No (default 3) |

**Submit action:**
- `POST /api/v1/generation/guided-campaign` with `source_mode: "guided_campaign"`
- WebSocket connection on `ws://api/v1/generation/{job_id}/stream` for streaming progress updates

---

### 4.3 AI对话 — AI Chat (`/chat`)

A conversational interface powered by the `founder_copilot` agent. The merchant describes content needs in natural Chinese and receives complete note packages within the conversation.

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│  Conversation History Sidebar (240px) │  Chat Area           │
│  ┌────────────────────────────────┐   │                      │
│  │ [+ 新对话]                     │   │  ┌──────────────┐    │
│  │                                │   │  │ AI助手        │    │
│  │ 今天                           │   │  │ 你好！我是你的│    │
│  │ ├─ 防晒霜春季推广              │   │  │ AI内容助手，  │    │
│  │ ├─ 口红新品上架                │   │  │ 告诉我你需要  │    │
│  │                                │   │  │ 什么样的内容？│    │
│  │ 昨天                           │   │  └──────────────┘    │
│  │ ├─ 38节活动笔记                │   │                      │
│  │ ├─ 竞品分析讨论                │   │  ┌──────────────┐    │
│  │                                │   │  │ 我            │    │
│  │ 3月10日                        │   │  │ 帮我做一条    │    │
│  │ ├─ 新用户引流方案              │   │  │ 针对25-30岁   │    │
│  │                                │   │  │ 职场女性的    │    │
│  │ ...                            │   │  │ 防晒霜笔记    │    │
│  └────────────────────────────────┘   │  └──────────────┘    │
│                                       │                      │
│                                       │  ┌──────────────┐    │
│                                       │  │ AI助手 (正在  │    │
│                                       │  │ 生成...)      │    │
│                                       │  │               │    │
│                                       │  │ [Streaming    │    │
│                                       │  │  response]    │    │
│                                       │  │               │    │
│                                       │  │ ┌──────────┐  │    │
│                                       │  │ │NoteCard  │  │    │
│                                       │  │ │(embedded)│  │    │
│                                       │  │ │[审核][编辑│  │    │
│                                       │  │ │ ][导出]   │  │    │
│                                       │  │ └──────────┘  │    │
│                                       │  └──────────────┘    │
│                                       │                      │
│                                       │  ┌──────────────────┐│
│                                       │  │ [输入消息...]     ││
│                                       │  │            [发送] ││
│                                       │  └──────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

**Key interactions:**
- **Send message** → `POST /api/v1/chat/conversations/{id}/messages` with message text
- **Streaming response** → WebSocket at `ws://api/v1/chat/conversations/{id}/stream`
- **Generated content cards** are embedded inline within AI response bubbles
- Quick action buttons on generated cards: 审核 (Review) → `/review/{id}`, 编辑 (Edit) → `/factory/{id}`, 导出 (Export) → export modal
- **Conversation history** loaded via `GET /api/v1/chat/conversations`

**Chat features:**
| Feature | Description |
|---|---|
| **Streaming text** | Responses stream token-by-token in real time via WebSocket |
| **Embedded note cards** | When the AI generates a note package, it renders as an interactive `NotePackageCard` inside the chat bubble |
| **Iterative refinement** | Merchant can say "换个标题" or "再活泼一点" and the AI refines the previous output |
| **Context awareness** | The Founder Copilot agent has access to the merchant's product catalog, brand rules, and recent generation history |
| **Quick templates** | Suggestion chips above the input: "节日促销", "新品上架", "用户好评", "竞品对比" |

---

### 4.4 我的产品库 — My Products (`/products`)

The merchant's product catalog and brand asset management hub.

**Product List Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│  Header: "我的产品库" + [+ 添加产品] + [Grid │ List] toggle  │
├──────────────────────────────────────────────────────────────┤
│  Search Bar: [🔍 搜索产品名称、类目...]                       │
│  Filters: [类目 ▾] [状态 ▾]                                 │
├──────────────────────────────────────────────────────────────┤
│  Grid View:                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │ Product Image │ │ Product Image │ │ Product Image │         │
│  │              │ │              │ │              │         │
│  ├──────────────┤ ├──────────────┤ ├──────────────┤         │
│  │ 防晒霜SPF50+ │ │ 口红色号101  │ │ 面膜套装     │         │
│  │ 美妆 · 护肤  │ │ 美妆 · 彩妆  │ │ 美妆 · 护肤  │         │
│  │ 笔记: 47     │ │ 笔记: 23     │ │ 笔记: 12     │         │
│  │ 素材: 2026Q1 │ │ 素材: 2026Q1 │ │ 素材: 2025Q4 │         │
│  └──────────────┘ └──────────────┘ └──────────────┘         │
└──────────────────────────────────────────────────────────────┘
```

**Product Detail Page (`/products/:id`):**

```
┌──────────────────────────────────────────────────────────────┐
│  Breadcrumb: 我的产品库 > 防晒霜SPF50+                       │
├──────────────────────────────────────────────────────────────┤
│  Product Header                                              │
│  ┌────────┐  名称: 防晒霜SPF50+                              │
│  │ Product│  类目: 美妆 > 护肤 > 防晒                        │
│  │ Image  │  状态: ● 活跃                                    │
│  │        │  [编辑] [生成笔记]                                │
│  └────────┘                                                  │
├──────────────────────────────────────────────────────────────┤
│  Tabs: [基本信息] [卖点] [素材包] [生成历史]                  │
│                                                              │
│  基本信息 Tab:                                               │
│  ├─ 描述: 轻薄不油腻的物理防晒霜...                          │
│  ├─ 价格: ¥128                                               │
│  ├─ 目标人群: 都市白领, 敏感肌女性                            │
│  └─ 竞品参考: [品牌A防晒霜] [品牌B防晒霜]                    │
│                                                              │
│  卖点 Tab:                                                   │
│  ├─ SPF50+ PA++++ ✅ 已验证                                  │
│  ├─ 物理防晒不刺激 ✅ 已验证                                  │
│  ├─ 成膜快不搓泥 ✅ 已验证                                    │
│  └─ [+ 添加卖点]                                             │
│                                                              │
│  素材包 Tab:                                                 │
│  └─ (See Asset Management below)                             │
│                                                              │
│  生成历史 Tab:                                               │
│  └─ Timeline of generated note packages for this product     │
└──────────────────────────────────────────────────────────────┘
```

**Asset Management (`/products/:id/assets`):**

```
┌──────────────────────────────────────────────────────────────┐
│  Quarterly Asset Pack Timeline                               │
│  [2025Q3] → [2025Q4] → [2026Q1 ● 当前] → [2026Q2 ○ 草稿]  │
├──────────────────────────────────────────────────────────────┤
│  2026Q1 素材包                                               │
│  状态: ✅ 已审核  |  上传于: 2026-01-05  |  素材数: 24       │
├──────────────────────────────────────────────────────────────┤
│  Asset Categories (tabs):                                    │
│  [产品照] [抠图] [Logo] [包装参考]                            │
│                                                              │
│  产品照 (Packshots):                                         │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────────────────┐            │
│  │ 📷 │ │ 📷 │ │ 📷 │ │ 📷 │ │  + 拖拽上传    │            │
│  │    │ │    │ │    │ │    │ │  或点击选择    │            │
│  │ ✅ │ │ ✅ │ │ ✅ │ │ ⏳ │ │                │            │
│  └────┘ └────┘ └────┘ └────┘ └────────────────┘            │
│                                                              │
│  抠图 (Cutouts):                                             │
│  ┌────┐ ┌────┐ ┌────────────────┐                            │
│  │ ✂️ │ │ ✂️ │ │  + 拖拽上传    │                            │
│  │    │ │    │ │                │                            │
│  │ ✅ │ │ ✅ │ │                │                            │
│  └────┘ └────┘ └────────────────┘                            │
└──────────────────────────────────────────────────────────────┘
```

**Data requirements:**
- Product list: `GET /api/v1/products`
- Product detail: `GET /api/v1/products/{id}`
- Asset packs: `GET /api/v1/products/{id}/asset-packs`
- Assets: `GET /api/v1/asset-packs/{packId}/assets`
- Upload: `POST /api/v1/asset-packs/{packId}/assets` (multipart)

---

### 4.5 内容工厂 — Content Factory (`/factory`)

The comprehensive view of all generated note packages across all products, modes, and statuses.

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│  Header: "内容工厂" + Stats: 总计 1,247 | 待审核 89 | 已发布 523│
├──────────────────────────────────────────────────────────────┤
│  Advanced Filter Bar                                         │
│  [状态 ▾] [来源 ▾] [产品 ▾] [日期范围 📅] [合规 ▾] [审核 ▾] │
│  [🔍 搜索标题关键词...]                                       │
├──────────────────────────────────────────────────────────────┤
│  Bulk Action Bar (visible when items selected)               │
│  [☑ 已选 5 项]  [批量审核 ✓] [批量拒绝 ✗] [批量导出 →]      │
├──────────────────────────────────────────────────────────────┤
│  Content Table / Card Grid (toggle)                          │
│                                                              │
│  Table View:                                                 │
│  ┌────┬──────────┬────────┬──────┬──────┬──────┬──────┬────┐ │
│  │ ☐  │ 封面/标题 │ 产品   │ 来源 │ 风格 │ 评分 │ 合规 │ 状态│ │
│  ├────┼──────────┼────────┼──────┼──────┼──────┼──────┼────┤ │
│  │ ☐  │ 🖼️ 这支防 │ 防晒霜 │ 每日 │ 水彩 │ 0.87 │ ✅   │ 待审│ │
│  │ ☐  │ 🖼️ 成分党 │ 防晒霜 │ 对话 │ 扁平 │ 0.82 │ ✅   │ 已批│ │
│  │ ☐  │ 🖼️ 闺蜜推 │ 口红   │ 一键 │ 拼贴 │ 0.76 │ ⚠️   │ 待审│ │
│  └────┴──────────┴────────┴──────┴──────┴──────┴──────┴────┘ │
│  Pagination: [← 上一页] 第 1/63 页 [下一页 →]               │
└──────────────────────────────────────────────────────────────┘
```

**Note Package Detail (`/factory/:id`):**

```
┌──────────────────────────────────────────────────────────────┐
│  Breadcrumb: 内容工厂 > np_20260312_a1b2c3                  │
├──────────────────────────────────────────────────────────────┤
│  Note Preview (left, 40%)     │  Metadata (right, 60%)       │
│  ┌──────────────────────┐     │                              │
│  │                      │     │  状态: ● 待审核              │
│  │  XiaoHongShu-style   │     │  产品: 防晒霜SPF50+          │
│  │  note preview        │     │  来源: 每日自动生成           │
│  │  (cover image at     │     │  风格: 水彩风                │
│  │   actual 3:4 ratio)  │     │  人设: 小美文案 v3           │
│  │                      │     │  综合评分: 0.87              │
│  │  Title: 这支防晒霜让 │     │  ├─ 预测互动: 0.73          │
│  │  我整个夏天都在线！   │     │  ├─ 风格多样性: 0.85        │
│  │                      │     │  └─ 品牌契合: 0.92          │
│  │  Body preview...     │     │                              │
│  │                      │     │  合规状态:                   │
│  │  #防晒霜推荐         │     │  ├─ 规则引擎: ✅ 通过        │
│  │  #夏日防晒           │     │  ├─ 模型分类: ✅ 通过        │
│  │                      │     │  └─ 人工审核: ⏳ 待审核      │
│  └──────────────────────┘     │                              │
├───────────────────────────────┤  Actions:                    │
│  Variants Section             │  [通过] [拒绝] [编辑] [导出] │
│                               │                              │
│  标题变体:                    ├──────────────────────────────┤
│  1. 这支防晒霜让我整个...     │  Carousel Images             │
│     (personal_story) ○        │  ┌────┐ ┌────┐ ┌────┐       │
│  2. 成分党狂喜！终于...       │  │ p1 │ │ p2 │ │ p3 │       │
│     (ingredient_focus) ●      │  └────┘ └────┘ └────┘       │
│                               │                              │
│  正文变体:                    │  Hashtags:                   │
│  1. 姐妹们！！我真的要...     │  #防晒霜推荐 #夏日防晒       │
│     (闺蜜聊天, 280字) ●       │  #成分党 #敏感肌防晒         │
│                               │                              │
│  首条评论:                    │  CTA: 搜索「XX防晒霜」       │
│  "姐妹们有什么防晒问题..."    │                              │
└──────────────────────────────────────────────────────────────┘
```

**Data requirements:**
- List: `GET /api/v1/note-packages` with filter parameters
- Detail: `GET /api/v1/note-packages/{id}`

**Advanced filters:**
| Filter | API Parameter | Type |
|---|---|---|
| 状态 (Status) | `status` | Multi-select enum |
| 来源 (Source) | `source_mode` | Multi-select: daily_auto, on_demand, guided_campaign |
| 产品 (Product) | `product_id` | Dropdown |
| 日期范围 (Date) | `created_after`, `created_before` | Date range picker |
| 合规 (Compliance) | `compliance_status` | Multi-select: pass, review, fail |
| 审核 (Review) | `review_status` | Multi-select: pending, approved, rejected |

---

### 4.6 待审核 — Pending Review (`/review`)

The approval workflow queue. Optimized for rapid, confident decision-making with compliance context always visible.

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│  Header: "待审核" + Queue Count: 待处理 23 件                 │
│  Priority: [全部] [合规警告优先] [高分优先] [最新优先]        │
├──────────────────────────────────────────────────────────────┤
│  Review Queue (left, 35%)     │  Review Panel (right, 65%)   │
│  ┌──────────────────────┐     │  ┌──────────────────────────┐│
│  │ ● np_...c3  0.87     │     │  │  Note Preview    │ Compli││
│  │   防晒霜 · 水彩风    │     │  │  ┌────────────┐  │ ance  ││
│  │   ✅ Pass             │ ←── │  │  │            │  │ Report││
│  ├──────────────────────┤     │  │  │ Cover      │  │       ││
│  │ ○ np_...d4  0.82     │     │  │  │ Image      │  │ ✅ 规则││
│  │   口红 · 扁平矢量    │     │  │  │ (3:4)      │  │   引擎││
│  │   ⚠️ Review           │     │  │  │            │  │ ✅ 模型││
│  ├──────────────────────┤     │  │  └────────────┘  │   分类││
│  │ ○ np_...e5  0.76     │     │  │                  │       ││
│  │   面膜 · 拼贴风      │     │  │  Title...        │ ⚠️ 警告││
│  │   ✅ Pass             │     │  │  Body...         │ "近似 ││
│  ├──────────────────────┤     │  │                  │  夸大" ││
│  │ ...                  │     │  │  #tags           │       ││
│  └──────────────────────┘     │  └──────────────────────────┘│
│                               │                              │
│                               │  ┌──────────────────────────┐│
│                               │  │  [✓ 通过]  [✗ 拒绝]      ││
│                               │  │  拒绝原因: [下拉选择]     ││
│                               │  │  备注: [可选文本框]       ││
│                               │  └──────────────────────────┘│
│  ┌──────────────────────┐     │                              │
│  │ Batch: [全选] [批量  │     │                              │
│  │ 通过] [批量拒绝]     │     │                              │
│  └──────────────────────┘     │                              │
└──────────────────────────────────────────────────────────────┘
```

**Key interactions:**
- **Click queue item** → loads note preview + compliance report in the right panel
- **通过 (Approve)** → `PATCH /api/v1/note-packages/{id}/review` action: `approve`
- **拒绝 (Reject)** → expand rejection reason, then `PATCH` with action: `reject` and `reason`
- **Batch actions** → select multiple items via checkboxes, bulk approve/reject
- **Keyboard shortcuts**: `A` = approve, `R` = reject, `↓` = next item (for rapid review)

**Compliance Report Panel:**
| Section | Content |
|---|---|
| 规则引擎 (Layer 1) | Pass/Fail with specific rule IDs for any triggers |
| 模型分类 (Layer 2) | Pass/Review/Fail with classifier findings and confidence scores |
| 合规警告 | Highlighted warnings with explanations in Chinese |
| 建议修改 | Suggested edits to resolve compliance issues |

---

### 4.7 投放中心 — Distribution Center (`/distribution`)

Export management for different XiaoHongShu distribution surfaces.

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│  Header: "投放中心"                                          │
├──────────────────────────────────────────────────────────────┤
│  Channel Tabs: [笔记导出] [聚光投放] [蒲公英合作]            │
├──────────────────────────────────────────────────────────────┤
│  笔记导出 Tab:                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Ready to Export: 15 note packages                   │    │
│  │                                                      │    │
│  │  ┌────────────────────────────────────────────┐      │    │
│  │  │ ☐ 防晒霜 · 这支防晒霜让我...  2026-03-12  │      │    │
│  │  │   文案 ✅ | 图片 ✅ | 标签 ✅              │      │    │
│  │  │   [下载包] [复制文案]                       │      │    │
│  │  ├────────────────────────────────────────────┤      │    │
│  │  │ ☐ 口红 · 成分党狂喜！...    2026-03-12    │      │    │
│  │  │   文案 ✅ | 图片 ✅ | 标签 ✅              │      │    │
│  │  │   [下载包] [复制文案]                       │      │    │
│  │  └────────────────────────────────────────────┘      │    │
│  │                                                      │    │
│  │  [批量下载已选] [导出CSV]                            │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Export History:                                             │
│  ┌──────┬──────────┬──────┬──────┬───────┐                  │
│  │ 日期 │ 内容     │ 渠道 │ 数量 │ 状态  │                  │
│  ├──────┼──────────┼──────┼──────┼───────┤                  │
│  │ 3/11 │ 防晒专题 │ 笔记 │ 5    │ ✅ 完成│                  │
│  │ 3/10 │ 口红推广 │ 聚光 │ 3    │ ✅ 完成│                  │
│  └──────┴──────────┴──────┴──────┴───────┘                  │
└──────────────────────────────────────────────────────────────┘
```

**Export bundles per channel (from Architecture § 6.8):**

| Channel | Bundle Contents |
|---|---|
| **笔记-ready** | Cover image (1:1 or 3:4), title (≤20 chars), body (≤1000 chars), hashtags, @mentions, first comment |
| **聚光-ready** | Ad creative image, headline, description, CTA, targeting metadata, bid suggestions |
| **蒲公英-ready** | Brief document, reference creatives, talking points, KOL/KOC matching tags, budget range |

**Data requirements:**
- Exportable packages: `GET /api/v1/note-packages?status=approved&exported=false`
- Create export: `POST /api/v1/exports` with `channel`, `note_package_ids`
- Export history: `GET /api/v1/exports`
- Download bundle: `GET /api/v1/exports/{id}/download`

---

### 4.8 达人合作 — Creator Collaboration (`/creators`)

Management hub for 蒲公英-ready creator briefs.

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│  Header: "达人合作" + [+ 新建简报]                            │
├──────────────────────────────────────────────────────────────┤
│  Tabs: [简报管理] [简报模板]                                  │
├──────────────────────────────────────────────────────────────┤
│  Brief List:                                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ 防晒霜春季推广简报                      2026-03-10    │  │
│  │ 产品: 防晒霜SPF50+  |  达人类型: 美妆博主, 成分党     │  │
│  │ 预算: ¥500-3,000/篇  |  状态: 🟢 已发送              │  │
│  │ [查看] [编辑] [导出蒲公英格式] [复制]                  │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ 口红新色号体验简报                      2026-03-08    │  │
│  │ 产品: 口红色号101  |  达人类型: 时尚博主, 日常分享     │  │
│  │ 预算: ¥1,000-5,000/篇  |  状态: 🟡 草稿              │  │
│  │ [查看] [编辑] [导出蒲公英格式] [复制]                  │  │
│  └────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│  Brief Detail (expanded or separate page):                   │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  产品概述: 轻薄物理防晒，SPF50+ PA++++...            │    │
│  │  目标人群: 25-35岁都市女性，敏感肌                    │    │
│  │  必须提及: SPF50+, 不闷痘, 成膜快                    │    │
│  │  视觉方向: 清新自然，户外场景                        │    │
│  │  品牌禁忌: 不提竞品, 不用"最"等绝对化用语            │    │
│  │  参考标题: "这支防晒霜让我整个夏天都在线！"          │    │
│  │  参考标签: #防晒霜推荐 #成分党                       │    │
│  │  合作形式: 图文笔记                                  │    │
│  │  预算范围: ¥500 - ¥3,000                             │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

**Data requirements:**
- Brief list: `GET /api/v1/exports?channel=蒲公英` (briefs are a type of export)
- Brief CRUD via export endpoints
- Brief template builder leverages `creator_brief_ready` data from `NotePackage` schema

---

### 4.9 成效分析 — Performance Analytics (`/analytics`)

Dashboard for tracking content performance across all published notes.

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│  Header: "成效分析" + Date Range Picker: [最近7天 ▾]         │
├──────────────────────────────────────────────────────────────┤
│  KPI Summary Cards (horizontal row)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ 曝光量   │ │ 点击量   │ │ 收藏量   │ │ 评论量   │       │
│  │ 125,430  │ │ 8,721    │ │ 3,456    │ │ 1,234    │       │
│  │ ↑ 12%    │ │ ↑ 8%     │ │ ↑ 15%    │ │ ↓ 3%     │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐                                  │
│  │ 转化量   │ │ 疲劳指数 │                                  │
│  │ 456      │ │ 0.23     │                                  │
│  │ ↑ 22%    │ │ 🟢 健康  │                                  │
│  └──────────┘ └──────────┘                                  │
├──────────────────────────────────────────────────────────────┤
│  Trend Chart (large area chart)                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │     曝光 ── 点击 ── 收藏                              │    │
│  │  ╱──╲                                                │    │
│  │ ╱    ╲──╱──╲                                         │    │
│  │╱           ╲──                                       │    │
│  │  3/6  3/7  3/8  3/9  3/10  3/11  3/12               │    │
│  └──────────────────────────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────┤
│  Two-Column Layout:                                          │
│                                                              │
│  Best Performing Styles       │  Best Performing Angles      │
│  ┌──────────────────────┐     │  ┌──────────────────────┐    │
│  │ 1. 水彩风    CTR 4.2%│     │  │ 1. 成分党    Save 8% │    │
│  │ 2. 扁平矢量  CTR 3.8%│     │  │ 2. 个人故事  Save 6% │    │
│  │ 3. 极简线条  CTR 3.1%│     │  │ 3. 好物清单  Save 5% │    │
│  └──────────────────────┘     │  └──────────────────────┘    │
│                                                              │
│  Product Comparison           │  Fatigue Indicators          │
│  ┌──────────────────────┐     │  ┌──────────────────────┐    │
│  │ (Bar chart comparing │     │  │ 防晒霜: 0.23 🟢      │    │
│  │  products by metric) │     │  │ 口红:   0.45 🟡      │    │
│  └──────────────────────┘     │  │ 面膜:   0.12 🟢      │    │
│                               │  └──────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

**Data requirements:**
- Overview metrics: `GET /api/v1/analytics/overview?period=7d`
- Trend data: `GET /api/v1/analytics/trends?metric=impressions&period=7d&granularity=daily`
- Product comparison: `GET /api/v1/analytics/products`
- Style performance: `GET /api/v1/analytics/overview` (includes `top_styles`, `top_hooks`)
- Fatigue scores: `GET /api/v1/analytics/fatigue`

**Drill-down pages:**
- `/analytics/products/:id` — product-level deep-dive with per-note metrics
- `/analytics/notes/:id` — single note performance with daily trend

---

### 4.10 品牌规则 — Brand Rules (`/rules`)

Merchant configuration center for brand identity, compliance, and review workflow.

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│  Header: "品牌规则"                                          │
├──────────────────────────────────────────────────────────────┤
│  Tabs: [语气预设] [禁用词] [必须卖点] [合规设置] [审核模式]   │
├──────────────────────────────────────────────────────────────┤
│  语气预设 (Tone Presets) Tab:                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  当前活跃: 🟢 闺蜜聊天                               │    │
│  │                                                      │    │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐       │    │
│  │  │ 闺蜜聊天 🟢│ │ 专业测评   │ │ 种草安利   │       │    │
│  │  │ 亲切、口语 │ │ 客观、数据 │ │ 热情、推荐 │       │    │
│  │  │ 化、emoji  │ │ 驱动、对比 │ │ 感、体验式 │       │    │
│  │  │ 丰富      │ │ 评测      │ │ 描述      │       │    │
│  │  │ [激活] [编辑│ │ [激活] [编辑│ │ [激活] [编辑│       │    │
│  │  │ ]         │ │ ]         │ │ ]         │       │    │
│  │  └────────────┘ └────────────┘ └────────────┘       │    │
│  │  ┌────────────┐ ┌──────────────┐                     │    │
│  │  │ 干货分享   │ │ + 自定义语气 │                     │    │
│  │  │ 实用、步骤 │ │              │                     │    │
│  │  │ 清晰、教程 │ │              │                     │    │
│  │  │ 风格      │ │              │                     │    │
│  │  │ [激活] [编辑│ │              │                     │    │
│  │  │ ]         │ │              │                     │    │
│  │  └────────────┘ └──────────────┘                     │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  禁用词 (Banned Words) Tab:                                  │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  平台禁用词 (不可编辑): 最, 第一, 国家级, 顶级...     │    │
│  │  行业禁用词 (不可编辑): 疗效, 根治, 药用...           │    │
│  │                                                      │    │
│  │  自定义禁用词:                                        │    │
│  │  [最好] [超级] [绝对] [永久] [+ 添加]                 │    │
│  │                                                      │    │
│  │  导入/导出: [从CSV导入] [导出列表]                    │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  审核模式 (Review Mode) Tab:                                 │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  审核策略:                                            │    │
│  │  (●) 全量审核 — 所有内容必须人工审核                   │    │
│  │  (○) 抽样审核 — 高分内容自动通过，低分人工审核         │    │
│  │  (○) 自动审核 — 合规通过即自动批准                     │    │
│  │                                                      │    │
│  │  自动审核阈值 (仅抽样/自动模式):                      │    │
│  │  合规评分 ≥ [85] 且 排名评分 ≥ [0.75]                 │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

**Data requirements:**
- Merchant rules: `GET /api/v1/merchants/{id}/rules`
- Update rules: `PUT /api/v1/merchants/{id}/rules`
- Tone presets are part of `MerchantRules.tone_presets`
- Banned words include platform-level (read-only) and merchant-level (editable)

---

## 5. Shared Component Architecture

Reusable components live in `packages/ui/` and are consumed by `apps/web`. Components follow atomic design principles.

### 5.1 Core Business Components

| Component | Location | Description | Used By |
|---|---|---|---|
| `NotePackageCard` | `packages/ui/src/note-package-card/` | Card showing cover image (3:4), title, ranking score badge, style tag, compliance status, and quick action buttons. Supports compact (grid) and expanded (detail) variants. | Dashboard, Factory, Chat, Generate results |
| `NotePreview` | `packages/ui/src/note-preview/` | Full XiaoHongShu-style note preview at actual platform aspect ratios. Renders cover, carousel, title, body, hashtags, and first comment exactly as they'd appear on XiaoHongShu. | Review, Factory detail |
| `ComplianceStatusBadge` | `packages/ui/src/compliance-badge/` | Color-coded badge: green ✅ (pass), yellow ⚠️ (review), red ❌ (fail), gray ⏳ (pending). Optionally shows tooltip with findings summary. | All pages showing note packages |
| `RankingScoreBadge` | `packages/ui/src/ranking-badge/` | Circular or pill badge showing composite score (0-100). Color gradient: red (<50) → yellow (50-75) → green (>75). | Dashboard, Factory, Review |
| `StyleFamilySelector` | `packages/ui/src/style-family-selector/` | Visual grid of 6 style families, each with a thumbnail preview. Single-select or multi-select mode. | Generate form, Factory filters |
| `AssetUploader` | `packages/ui/src/asset-uploader/` | Drag-and-drop zone supporting multi-file upload. Shows upload progress, thumbnail previews, and validation errors (format, size). Accepts images (JPEG, PNG, WebP). | Product assets page |
| `ChatMessage` | `packages/ui/src/chat-message/` | Chat bubble with user/AI distinction, streaming text support, and slots for embedded components (note cards, action buttons). | Chat page |
| `GenerationForm` | `packages/ui/src/generation-form/` | The complete Guided Campaign form with all fields from PRD § 4.3. Uses `react-hook-form` for validation. Supports dynamic field visibility (e.g., 聚光 fields appear when toggle is on). | Generate page |
| `ReviewPanel` | `packages/ui/src/review-panel/` | Side-by-side layout: note preview on left, compliance report on right. Includes approve/reject buttons with reason input. | Review page |
| `PerformanceChart` | `packages/ui/src/performance-chart/` | Configurable chart component supporting line, bar, and area charts. Handles daily/weekly/monthly granularity. Chinese locale for dates and numbers. | Analytics page |

### 5.2 Utility Components

| Component | Description |
|---|---|
| `TagInput` | Multi-value tag input for banned words, selling points, audience tags. Supports autocomplete suggestions. |
| `FilterBar` | Horizontal filter bar with dropdowns, date pickers, and search. Persists filter state to URL params. |
| `DataTable` | Sortable, filterable table with checkbox selection, pagination, and bulk actions. |
| `EmptyState` | Illustrated empty state for pages/sections with no data. Chinese copy. |
| `LoadingState` | Skeleton loaders matching the layout of the component being loaded. |
| `ConfirmDialog` | Confirmation modal for destructive actions (reject, delete). Chinese labels. |
| `ToastNotification` | Toast notifications for success/error/info. Position: top-right. |
| `Breadcrumb` | Breadcrumb navigation with Chinese labels. Auto-generated from route. |
| `PageHeader` | Consistent page header with title, subtitle, and action buttons. |
| `StatusBadge` | Generic status indicator for various entity states (draft, active, archived). |

### 5.3 Component Hierarchy

```
AppShell
├── NavigationRail
│   ├── Logo
│   ├── NavGroup ("CONTENT")
│   │   ├── NavItem (今日推荐)
│   │   ├── NavItem (一键生成)
│   │   └── NavItem (AI对话)
│   ├── NavGroup ("ASSETS")
│   │   └── NavItem (我的产品库)
│   ├── NavGroup ("OPERATIONS")
│   │   ├── NavItem (内容工厂)
│   │   ├── NavItem (待审核) + Badge (count)
│   │   └── NavItem (投放中心)
│   ├── NavGroup ("INTELLIGENCE")
│   │   ├── NavItem (达人合作)
│   │   ├── NavItem (成效分析)
│   │   └── NavItem (品牌规则)
│   └── AccountMenu
│       ├── Avatar + Name
│       ├── MenuItem (账号设置)
│       └── MenuItem (退出登录)
├── ContentArea
│   ├── PageHeader
│   ├── FilterBar (when applicable)
│   └── PageContent (route-specific)
└── GlobalOverlays
    ├── ToastContainer
    ├── ModalContainer
    └── CommandPalette (Ctrl+K)
```

---

## 6. Design System Notes

### 6.1 Typography

| Level | Font | Size | Weight | Usage |
|---|---|---|---|---|
| Display | System Chinese (PingFang SC, Noto Sans SC, Microsoft YaHei) | 32px | 700 | Page titles |
| Heading 1 | System Chinese | 24px | 600 | Section headers |
| Heading 2 | System Chinese | 20px | 600 | Subsection headers |
| Body | System Chinese | 14px | 400 | Default text |
| Body Small | System Chinese | 12px | 400 | Secondary info, timestamps |
| Caption | System Chinese | 11px | 400 | Labels, badges |
| Monospace | JetBrains Mono, Menlo | 13px | 400 | Code, IDs, scores |

Font stack for Tailwind:

```css
fontFamily: {
  sans: [
    '"PingFang SC"',
    '"Noto Sans SC"',
    '"Microsoft YaHei"',
    '"Helvetica Neue"',
    'Arial',
    'sans-serif',
  ],
}
```

### 6.2 Color Palette

| Token | Hex | Usage |
|---|---|---|
| `primary-50` – `primary-900` | Warm coral/rose gradient | Primary actions, active navigation |
| `primary-500` | `#E8554E` | Primary button, active tab |
| `primary-600` | `#D44840` | Primary hover |
| `neutral-50` – `neutral-900` | Warm gray gradient | Backgrounds, borders, text |
| `neutral-50` | `#FAFAF9` | Page background |
| `neutral-100` | `#F5F5F4` | Card background |
| `neutral-200` | `#E7E5E4` | Borders |
| `neutral-800` | `#292524` | Primary text |
| `neutral-500` | `#78716C` | Secondary text |
| `success` | `#22C55E` | Approved, pass, healthy |
| `warning` | `#F59E0B` | Review needed, caution |
| `error` | `#EF4444` | Failed, rejected |
| `info` | `#3B82F6` | Informational |

The palette uses **warm undertones** (stone/amber family) rather than cold blue-grays, creating a creative workspace feel appropriate for marketing content.

### 6.3 Spacing and Layout

| Token | Value | Usage |
|---|---|---|
| `space-1` | 4px | Tight inline spacing |
| `space-2` | 8px | Default inline spacing, icon padding |
| `space-3` | 12px | Card internal padding |
| `space-4` | 16px | Default component spacing |
| `space-6` | 24px | Section spacing |
| `space-8` | 32px | Page section gaps |
| `nav-rail-width` | 240px | Expanded navigation rail |
| `nav-rail-collapsed` | 64px | Collapsed navigation rail (icons only) |
| `content-max-width` | 1440px | Maximum content area width |
| `card-border-radius` | 12px | Card corners |
| `button-border-radius` | 8px | Button corners |

### 6.4 XiaoHongShu Preview Specifications

To render authentic note previews:

| Property | Value |
|---|---|
| Feed cover aspect ratio | 3:4 (1080 × 1440 px) |
| Search cover aspect ratio | 1:1 (1080 × 1080 px) |
| Title max length | 20 characters |
| Body max length | 1000 characters |
| Hashtag display | Inline, colored, tappable |
| First comment | Shown below body in preview |
| Font for preview | Simulated XiaoHongShu typography (system sans-serif at appropriate sizing) |

---

## 7. State Management

### 7.1 Strategy Overview

| State Category | Tool | Scope | Persistence |
|---|---|---|---|
| **Server state** | TanStack Query (React Query) v5 | API data: products, note packages, analytics | Cached with configurable stale time |
| **Client UI state** | Zustand | Navigation, filter state, modal state, layout preferences | sessionStorage for filter persistence |
| **Form state** | React Hook Form + Zod | Generation form, brand rules, product editor | Form-local; submitted via API |
| **Real-time state** | WebSocket (native or Socket.IO) | Chat messages, generation progress | In-memory; synced with server on reconnect |
| **Auth state** | Zustand + httpOnly cookies | JWT tokens, user profile, tenant context | Secure cookies for tokens; Zustand for profile |

### 7.2 TanStack Query Key Strategy

```typescript
const queryKeys = {
  products: {
    all:   ['products'] as const,
    list:  (filters: ProductFilters) => ['products', 'list', filters] as const,
    detail:(id: string) => ['products', 'detail', id] as const,
    assets:(id: string) => ['products', 'assets', id] as const,
  },
  notePackages: {
    all:    ['notePackages'] as const,
    list:   (filters: NotePackageFilters) => ['notePackages', 'list', filters] as const,
    detail: (id: string) => ['notePackages', 'detail', id] as const,
    daily:  (date: string) => ['notePackages', 'daily', date] as const,
  },
  analytics: {
    overview: (period: string) => ['analytics', 'overview', period] as const,
    trends:   (params: TrendParams) => ['analytics', 'trends', params] as const,
    fatigue:  () => ['analytics', 'fatigue'] as const,
  },
  chat: {
    conversations: () => ['chat', 'conversations'] as const,
    messages:      (convId: string) => ['chat', 'messages', convId] as const,
  },
  personas: {
    all:    ['personas'] as const,
    detail: (id: string) => ['personas', 'detail', id] as const,
  },
  teams: {
    all:    ['teams'] as const,
    detail: (id: string) => ['teams', 'detail', id] as const,
  },
} as const;
```

### 7.3 Zustand Store Structure

```typescript
interface UIStore {
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;

  activeFilters: Record<string, FilterState>;
  setFilter: (page: string, filter: FilterState) => void;
  clearFilters: (page: string) => void;

  selectedItems: Record<string, Set<string>>;
  toggleSelection: (page: string, id: string) => void;
  clearSelection: (page: string) => void;
}

interface AuthStore {
  user: User | null;
  tenant: Tenant | null;
  isAuthenticated: boolean;
  login: (credentials: LoginPayload) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

interface ChatStore {
  activeConversationId: string | null;
  pendingMessage: string;
  isStreaming: boolean;
  wsConnection: WebSocket | null;
  connect: (conversationId: string) => void;
  disconnect: () => void;
  sendMessage: (text: string) => void;
}

interface GenerationStore {
  activeJobId: string | null;
  progress: GenerationProgress | null;
  isGenerating: boolean;
  startGeneration: (request: GenerationRequest) => Promise<void>;
  cancelGeneration: () => void;
}
```

### 7.4 Real-Time Communication

| Channel | Protocol | Events |
|---|---|---|
| Chat messages | WebSocket | `message.new`, `message.chunk` (streaming), `message.complete` |
| Generation progress | WebSocket | `generation.started`, `generation.progress`, `generation.variant_ready`, `generation.complete`, `generation.failed` |
| Review updates | WebSocket | `review.new_item`, `review.status_changed` (for multi-user review) |

---

## 8. Admin Pages — Agent Team Management

These pages are accessible only to users with the `admin` RBAC role. They implement the UI described in AGENT_TEAM_SPEC § 10.

### 8.1 Agent Team Designer (`/admin/teams`)

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│  Header: "Agent团队设计" + [+ 新建团队] + [从预设创建]       │
├──────────────────────────────────────────────────────────────┤
│  Team List (cards or table)                                  │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  🟢 标准笔记团队 (v2.1)            当前活跃          │    │
│  │  8/8 必要角色 + 1 可选角色                           │    │
│  │  Researcher → Planner → Writer ∥ Visual → ...        │    │
│  │  [编辑] [复制] [版本历史]                            │    │
│  ├──────────────────────────────────────────────────────┤    │
│  │  ○ 增长优先团队 (v1.0)             备用              │    │
│  │  8/8 必要角色                                        │    │
│  │  [编辑] [激活] [复制]                                │    │
│  └──────────────────────────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────┤
│  Team Editor (full page at /admin/teams/:id):                │
│                                                              │
│  Collaboration Graph (top half — interactive DAG)            │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  [Copilot] → [Planner] → [Writer]─┐                 │    │
│  │                           [Visual]─┤→ [Compliance]   │    │
│  │                                    └→ [Ranker]       │    │
│  │                                       → [Packager]   │    │
│  │  (Nodes are draggable; edges show artifact types)    │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Role ↔ Persona Mapping (bottom half — table)                │
│  ┌──────────┬──────────────────┬──────────┬────────────┐     │
│  │ 角色     │ 绑定人设         │ 版本     │ 操作       │     │
│  ├──────────┼──────────────────┼──────────┼────────────┤     │
│  │ Copilot  │ 温暖顾问 v2      │ active   │ [换] [配置]│     │
│  │ Planner  │ 数据驱动策略 v1  │ active   │ [换] [配置]│     │
│  │ Writer   │ 闺蜜文案 v3      │ active   │ [换] [配置]│     │
│  │ Visual   │ 清新美学 v1      │ active   │ [换] [配置]│     │
│  │ ...      │ ...              │ ...      │ ...        │     │
│  └──────────┴──────────────────┴──────────┴────────────┘     │
│                                                              │
│  Validation Panel:                                           │
│  ✅ All required roles bound                                 │
│  ✅ No graph cycles detected                                 │
│  ✅ All persona versions are active                          │
│  [保存] [保存为新版本] [激活此团队]                           │
└──────────────────────────────────────────────────────────────┘
```

**Data requirements:**
- Team list: `GET /api/v1/agent-teams`
- Team detail: `GET /api/v1/agent-teams/{id}`
- Available roles: `GET /api/v1/agent-roles`
- Save team: `PUT /api/v1/agent-teams/{id}`
- Activate team: `PATCH /api/v1/agent-teams/{id}/activate`

### 8.2 Persona Library (`/admin/personas`)

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│  Header: "人设库" + [+ 新建人设] + [从模板创建]              │
│  Filters: [兼容角色 ▾] [标签 ▾] [语气风格 ▾]               │
├──────────────────────────────────────────────────────────────┤
│  Persona Card Grid:                                          │
│  ┌──────────────────┐ ┌──────────────────┐                   │
│  │ 🎭 闺蜜文案 v3   │ │ 🎭 温暖顾问 v2   │                   │
│  │                  │ │                  │                   │
│  │ "像闺蜜一样亲切  │ │ "温暖专业的品牌  │                   │
│  │  推荐好物"       │ │  顾问"           │                   │
│  │                  │ │                  │                   │
│  │ 兼容: Writer,    │ │ 兼容: Copilot    │                   │
│  │ Copilot          │ │                  │                   │
│  │ 标签: 种草, 口语 │ │ 标签: 专业, 温暖 │                   │
│  │ 正式度: ████░ 3/5│ │ 正式度: █████ 4/5│                   │
│  │ [编辑][克隆][版本]│ │ [编辑][克隆][版本]│                   │
│  └──────────────────┘ └──────────────────┘                   │
├──────────────────────────────────────────────────────────────┤
│  Persona Editor (at /admin/personas/:id):                    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  基本信息:                                            │    │
│  │  名称: [闺蜜文案]  标签: [种草] [口语] [+ 添加]       │    │
│  │  描述: [像闺蜜一样亲切推荐好物，用口语化表达...]       │    │
│  │  兼容角色: [☑ Writer] [☑ Copilot] [☐ Planner]        │    │
│  │                                                      │    │
│  │  行为参数:                                            │    │
│  │  正式度: ████░░░░░░ 3/10                              │    │
│  │  创意度: ██████░░░░ 6/10                              │    │
│  │  Emoji密度: ████████░░ 8/10                           │    │
│  │  句子长度: ████░░░░░░ 4/10 (偏短)                     │    │
│  │                                                      │    │
│  │  硬性约束:                                            │    │
│  │  [不使用网络流行语] [不提及竞品] [+ 添加]              │    │
│  │                                                      │    │
│  │  系统提示词预览:                                       │    │
│  │  ┌──────────────────────────────────────────┐         │    │
│  │  │ 你是一位亲切的闺蜜式文案专家。你的写作   │         │    │
│  │  │ 风格口语化、活泼，喜欢用emoji和感叹号。  │         │    │
│  │  │ 你推荐产品时像在跟好朋友分享心得...       │         │    │
│  │  └──────────────────────────────────────────┘         │    │
│  │                                                      │    │
│  │  [保存草稿] [发布新版本] [预览生成效果]               │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

**Data requirements:**
- Persona list: `GET /api/v1/personas`
- Persona detail: `GET /api/v1/personas/{id}`
- Persona versions: `GET /api/v1/personas/{id}/versions`
- Create/update: `POST/PUT /api/v1/personas`

### 8.3 Team Presets

Available at the top of the Agent Team Designer page. Presets are predefined team configurations from AGENT_TEAM_SPEC § 11.

| Preset | Chinese Name | Key Characteristics |
|---|---|---|
| Soft & Warm Brand Team | 温暖品牌团队 | Empathetic storytelling, warm watercolor visuals, 闺蜜 tone |
| Performance-First Growth Team | 增长优先团队 | Data-driven, conversion-focused, bold flat vector visuals |
| Premium Lifestyle Team | 高端生活方式团队 | Aspirational, elegant, minimal line art |
| Cute Cartoon-Focused Team | 可爱卡通团队 | Playful, youth-oriented, pixel art / pop art |

### 8.4 Experiment Dashboard (`/admin/experiments`)

**Layout:**

```
┌──────────────────────────────────────────────────────────────┐
│  Header: "实验面板" + [+ 新建A/B测试]                         │
├──────────────────────────────────────────────────────────────┤
│  Active Experiments:                                         │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  实验: Writer人设对比 — 闺蜜文案 v3 vs 种草达人 v2    │    │
│  │  角色: xhs_note_writer  |  流量分配: 50/50            │    │
│  │  运行时间: 7天  |  已生成: 142 vs 138 笔记包          │    │
│  │  状态: 🟡 运行中 (尚未达到统计显著性)                 │    │
│  │                                                      │    │
│  │  ┌─────────────┬──────────────┬──────────────┐        │    │
│  │  │ 指标        │ 闺蜜文案 v3  │ 种草达人 v2  │        │    │
│  │  ├─────────────┼──────────────┼──────────────┤        │    │
│  │  │ 互动率      │ 4.2%         │ 3.8%         │        │    │
│  │  │ 审核通过率  │ 72%          │ 68%          │        │    │
│  │  │ 编辑率      │ 35%          │ 42%          │        │    │
│  │  │ 合规通过率  │ 94%          │ 91%          │        │    │
│  │  └─────────────┴──────────────┴──────────────┘        │    │
│  │                                                      │    │
│  │  [查看详情] [结束实验] [选择获胜者]                    │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Past Experiments:                                           │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Visual人设对比  |  获胜: 清新美学 v1  |  2026-03-01  │    │
│  │  Planner人设对比  |  获胜: 数据驱动 v1  |  2026-02-15 │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

**Data requirements:**
- Experiment list: `GET /api/v1/agent-teams/experiments`
- Experiment detail: `GET /api/v1/agent-teams/experiments/{id}`
- Create experiment: `POST /api/v1/agent-teams/experiments`

---

## 9. Layout Structure

### 9.1 Root Layout

```
┌──────────────────────────────────────────────────────────────┐
│ ┌───────┐ ┌──────────────────────────────────────────────┐   │
│ │ Nav   │ │ Content Area                                 │   │
│ │ Rail  │ │                                              │   │
│ │       │ │  ┌──────────────────────────────────────┐    │   │
│ │ 240px │ │  │ Page Content (varies per route)      │    │   │
│ │       │ │  │                                      │    │   │
│ │       │ │  │ max-width: 1440px                    │    │   │
│ │       │ │  │ padding: 32px                        │    │   │
│ │       │ │  │                                      │    │   │
│ │       │ │  └──────────────────────────────────────┘    │   │
│ │       │ │                                              │   │
│ └───────┘ └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### 9.2 Auth Layout (Login / Onboarding)

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                  ┌──────────────────┐                        │
│                  │    GenPos Logo    │                        │
│                  │                  │                        │
│                  │  Login Form /    │                        │
│                  │  Onboarding      │                        │
│                  │  Wizard          │                        │
│                  │                  │                        │
│                  └──────────────────┘                        │
│                                                              │
│  (Centered card on warm gradient background)                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 10. Responsive Behavior

### 10.1 Breakpoints

| Breakpoint | Width | Behavior |
|---|---|---|
| Desktop Large | ≥ 1440px | Full layout, 4-column card grid, expanded nav rail |
| Desktop | 1024–1439px | Full layout, 3-column card grid, expanded nav rail |
| Tablet | 768–1023px | Collapsed nav rail (icons only), 2-column card grid, side panels become full-page |
| Mobile | < 768px | Bottom navigation bar (5 most-used tabs), single-column layout, all panels are full-page |

### 10.2 Mobile Navigation

On mobile (< 768px), the nav rail is replaced by a bottom tab bar showing the 5 most-used tabs:

| Position | Tab | Icon |
|---|---|---|
| 1 | 今日推荐 | ☀️ |
| 2 | 一键生成 | ⚡ |
| 3 | AI对话 | 💬 |
| 4 | 内容工厂 | 🏭 |
| 5 | 更多 (More) | ☰ |

The "更多" tab opens a drawer with access to all remaining tabs and settings.

### 10.3 Responsive Component Behavior

| Component | Desktop | Tablet | Mobile |
|---|---|---|---|
| `NotePackageCard` grid | 4 columns | 2 columns | 1 column |
| `ReviewPanel` | Side-by-side | Stacked (preview on top, report below) | Full-page views |
| `ChatMessage` sidebar | Visible (240px) | Drawer overlay | Drawer overlay |
| `DataTable` | Full table | Horizontal scroll | Card list |
| `GenerationForm` | 2-column | 2-column | Single column |
| `PerformanceChart` | Full width | Full width | Scrollable |
| `NavigationRail` | Expanded (240px) | Collapsed (64px icons) | Bottom bar |

---

## Appendix A: Page → API Endpoint Map

Quick reference for frontend developers connecting pages to backend endpoints.

| Page | Primary Endpoints |
|---|---|
| 今日推荐 | `GET /note-packages`, `PATCH /note-packages/{id}/review` |
| 一键生成 | `POST /generation/guided-campaign`, `WS /generation/{id}/stream` |
| AI对话 | `GET/POST /chat/conversations`, `WS /chat/conversations/{id}/stream` |
| 我的产品库 | `GET/POST /products`, `GET/PUT /products/{id}` |
| 素材管理 | `GET/POST /asset-packs`, `POST /asset-packs/{id}/assets` |
| 内容工厂 | `GET /note-packages`, `GET /note-packages/{id}` |
| 待审核 | `GET /note-packages?status=pending_review`, `PATCH /note-packages/{id}/review` |
| 投放中心 | `GET/POST /exports`, `GET /exports/{id}/download` |
| 达人合作 | `GET/POST /exports?channel=蒲公英` |
| 成效分析 | `GET /analytics/overview`, `GET /analytics/trends`, `GET /analytics/products`, `GET /analytics/fatigue` |
| 品牌规则 | `GET/PUT /merchants/{id}/rules` |
| Agent团队设计 | `GET/PUT /agent-teams`, `GET /agent-roles`, `PATCH /agent-teams/{id}/activate` |
| 人设库 | `GET/POST/PUT /personas`, `GET /personas/{id}/versions` |
| 实验面板 | `GET/POST /agent-teams/experiments` |

---

## Appendix B: Key User Flows

### B.1 Morning Review Flow

```
Merchant logs in
  → Lands on 今日推荐 (dashboard)
  → Sees today's auto-generated note packages ranked by score
  → Scans hero card (top pick)
  → Approves with one tap ✓
  → Scans remaining cards
  → Rejects one with reason "标题不够吸引"
  → Clicks "编辑" on another to tweak the title
  → → Navigates to /factory/{id}
  → → Edits title inline
  → → Saves and approves
  → Returns to dashboard, continues review
  → All items reviewed → redirect to 投放中心 for export
```

### B.2 On-Demand Generation Flow

```
Merchant opens AI对话 (chat)
  → Types: "帮我做一条针对25-30岁职场女性的防晒霜笔记"
  → AI streams a response with clarifying context
  → AI generates 3 note packages, rendered as inline cards
  → Merchant reviews cards in chat
  → Says: "第一个标题换一下，更活泼一点"
  → AI regenerates the first card with updated title
  → Merchant approves the card → note package moves to review queue
```

### B.3 Guided Campaign Flow

```
Merchant opens 一键生成 (generate)
  → Fills out structured form:
     Product: 防晒霜SPF50+
     Audience: 都市白领, 学生党
     Objective: 种草
     Style: 水彩风
     Variant count: 10
  → Clicks "开始生成"
  → Progress bar shows streaming generation
  → 10 note packages appear in a card grid below the form
  → Merchant reviews, approves 6, rejects 4
  → Approved packages enter the review queue
```

---

## Appendix C: Accessibility Notes

| Concern | Implementation |
|---|---|
| **Screen reader** | All interactive elements have `aria-label` in Chinese. Image cards have `alt` text describing content type. |
| **Keyboard navigation** | Full tab-order support. Review page supports `A`/`R`/`↓` shortcuts. Command palette via `Ctrl+K`. |
| **Color contrast** | All text meets WCAG AA contrast ratios against background. Status indicators use shape + color (not color alone). |
| **Motion** | Animations respect `prefers-reduced-motion`. Streaming text can be toggled to batch mode. |
| **Font scaling** | Layout accommodates up to 150% browser font scaling without overflow. |
