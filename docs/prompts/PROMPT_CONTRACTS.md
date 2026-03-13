# GenPos — Prompt Contracts

> **Version:** 0.1.0-draft
> **Last updated:** 2026-03-12
> **Status:** Living document — evolves with the system
> **Parent:** [ARCHITECTURE.md](../architecture/ARCHITECTURE.md) § 8 (Agent Runtime Architecture)
> **Sibling:** [AGENT_TEAM_SPEC.md](../architecture/AGENT_TEAM_SPEC.md) § 12 (Agent Input/Output Contracts)

---

## Table of Contents

1. [Prompt Architecture Overview](#1-prompt-architecture-overview)
2. [Strategy Planner Prompt Contract](#2-strategy-planner-prompt-contract)
3. [XiaoHongShu Note Writer Prompt Contract](#3-xiaohongshu-note-writer-prompt-contract)
4. [Cartoon Visual Agent Prompt Contract](#4-cartoon-visual-agent-prompt-contract)
5. [Compliance Agent Prompt Contract](#5-compliance-agent-prompt-contract)
6. [Ranking Agent Prompt Contract](#6-ranking-agent-prompt-contract)
7. [Founder Copilot Prompt Contract](#7-founder-copilot-prompt-contract)
8. [Prompt Versioning Rules](#8-prompt-versioning-rules)
9. [Persona Injection Pattern](#9-persona-injection-pattern)
10. [Structured Output Validation](#10-structured-output-validation)
11. [Prompt Template Examples](#11-prompt-template-examples)

---

## 1. Prompt Architecture Overview

Every LLM call in the GenPos pipeline is governed by a **prompt contract** — a formal specification of what goes into the prompt and what must come out. Prompt contracts sit between the typed pipeline artifacts (defined in `AGENT_TEAM_SPEC.md` § 12) and the raw LLM interaction. They ensure deterministic, auditable, and schema-validated generation at every agent step.

### 1.1 Design Principles

| Principle | Description |
|---|---|
| **Versioned templates** | All prompts are stored in the `prompt_versions` table. Each has a `prompt_family`, monotonic `version`, Jinja2 `template`, and declared `variables` schema. |
| **Schema-validated I/O** | Every prompt contract declares a strict JSON input schema and output schema. Inputs are validated before the LLM call; outputs are validated after. Malformed outputs trigger retry. |
| **Persona-agnostic templates** | Prompt templates define the role's operational instructions. Persona context is injected as a supplementary system-level prefix — never baked into the template body. |
| **Deterministic replay** | Every LLM call records `(prompt_version, model_version, input_hash, output_hash, timestamp)` for full lineage tracing and replay. |
| **Jinja2 variable binding** | Templates use `{{ variable_name }}` syntax. Variables are bound at runtime from the typed pipeline artifacts and merchant configuration. |

### 1.2 Prompt Composition Stack

Each LLM call is assembled from four layers, concatenated in order:

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Persona System Prefix (optional)              │
│  Injected from persona_context when a persona is bound. │
│  Shapes tone, vocabulary, and behavioral style.         │
│  NEVER alters the output schema or operational rules.   │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Role System Prompt                            │
│  Defines the agent's identity, responsibilities, and    │
│  output schema. Loaded from prompt_versions table.      │
│  Owned by platform engineering. Immutable per version.  │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Task Context (user/assistant messages)        │
│  Runtime data: product truth, strategy plan, merchant   │
│  rules, performance context, asset references.          │
│  Assembled from typed pipeline artifacts.               │
├─────────────────────────────────────────────────────────┤
│  Layer 4: Output Instruction                            │
│  Explicit JSON schema reminder and formatting rules.    │
│  Reinforces structured output requirements.             │
└─────────────────────────────────────────────────────────┘
```

### 1.3 Prompt Family Registry

Each agent role maps to one or more prompt families:

| Agent Role | Prompt Family | Description |
|---|---|---|
| `strategy_planner` | `strategy_planner_v1` | Creative strategy generation |
| `xhs_note_writer` | `xhs_note_writer_v1` | XiaoHongShu note text generation |
| `cartoon_visual_designer` | `cartoon_visual_v1` | Visual scene brief and image prompt generation |
| `compliance_reviewer` | `compliance_reviewer_v1` | Compliance evaluation and finding generation |
| `ranking_analyst` | `ranking_analyst_v1` | Creative variant scoring and ranking |
| `founder_copilot` | `founder_copilot_v1` | Intent parsing and job structuring |

### 1.4 Relationship to Pipeline Artifacts

Prompt contracts transform **pipeline input artifacts** into **pipeline output artifacts** via LLM calls. The contract specifies the subset of artifact data that enters the prompt (input schema) and the LLM output structure (output schema) that is then wrapped into the full typed artifact by the Agent Runtime.

```
Pipeline Artifact (e.g. StrategyPlan)
    │
    ▼
Prompt Input Schema ── extract relevant fields ──► LLM Prompt
    │                                                  │
    │                                          LLM Response
    │                                                  │
    ▼                                                  ▼
Prompt Output Schema ◄── validate & parse ──── Raw JSON Output
    │
    ▼
Pipeline Artifact (e.g. NoteContentSet) ── wrap with metadata
```

---

## 2. Strategy Planner Prompt Contract

**Prompt family:** `strategy_planner_v1`
**Agent role:** `strategy_planner`
**Upstream artifact:** `StructuredJobRequest`
**Downstream artifact:** `StrategyPlan`

The Strategy Planner receives product truth, merchant rules, and performance context, then produces a creative strategy that all downstream agents execute against.

### 2.1 Input Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "StrategyPlannerInput",
  "type": "object",
  "required": ["product", "merchant_rules"],
  "properties": {
    "product": {
      "type": "object",
      "required": ["name", "category", "description", "primary_objective"],
      "properties": {
        "name": {
          "type": "string",
          "description": "Product display name",
          "examples": ["玻尿酸保湿精华液"]
        },
        "category": {
          "type": "string",
          "description": "Product category for rule matching",
          "examples": ["护肤品", "美妆", "食品", "母婴"]
        },
        "description": {
          "type": "string",
          "description": "Product description with key attributes",
          "maxLength": 2000
        },
        "primary_objective": {
          "type": "string",
          "enum": ["seeding", "conversion", "awareness", "engagement"],
          "description": "Marketing objective from StructuredJobRequest"
        },
        "key_selling_points": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Ordered list of selling points from product catalog"
        },
        "price_range": {
          "type": ["string", "null"],
          "description": "Price range for positioning context",
          "examples": ["¥89-¥129"]
        },
        "target_demographics": {
          "type": ["string", "null"],
          "description": "Pre-defined target audience from product catalog"
        }
      }
    },
    "merchant_rules": {
      "type": "object",
      "required": ["tone_preset"],
      "properties": {
        "tone_preset": {
          "type": "string",
          "description": "Merchant-configured tone direction",
          "examples": ["种草安利", "专业测评", "闺蜜聊天", "干货分享"]
        },
        "banned_words": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Merchant-specific banned word list",
          "default": []
        },
        "required_claims": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Claims that MUST appear in the strategy",
          "default": []
        },
        "banned_claims": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Claims that MUST NOT appear",
          "default": []
        },
        "compliance_level": {
          "type": "string",
          "enum": ["strict", "standard", "relaxed"],
          "default": "standard"
        }
      }
    },
    "performance_context": {
      "type": "object",
      "description": "Historical performance signals from Analytics Service",
      "properties": {
        "recent_winners": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "angle": { "type": "string" },
              "hook_type": { "type": "string" },
              "style_family": { "type": "string" },
              "engagement_rate": { "type": "number" },
              "save_rate": { "type": "number" }
            }
          },
          "description": "Top-performing creative angles from the last 30 days"
        },
        "fatigued_angles": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "angle": { "type": "string" },
              "fatigue_score": { "type": "number", "minimum": 0, "maximum": 1 },
              "last_used": { "type": "string", "format": "date" }
            }
          },
          "description": "Angles showing declining engagement (fatigue_score > 0.7 = avoid)"
        },
        "trending_topics": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "topic": { "type": "string" },
              "relevance_score": { "type": "number" },
              "source": { "type": "string", "enum": ["xhs_trending", "industry_report", "competitor_analysis"] }
            }
          },
          "description": "Current trending topics relevant to the product category"
        }
      }
    },
    "persona_context": {
      "type": ["object", "null"],
      "description": "Optional persona overlay — injected as Layer 1 system prefix, not into the template body",
      "properties": {
        "communication_style": { "type": "string" },
        "decision_style": { "type": "string" },
        "tone_rules": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

### 2.2 Output Schema

The LLM **MUST** return valid JSON conforming to this schema. Responses that fail validation trigger up to 3 retries with escalating prompt specificity.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "StrategyPlannerOutput",
  "type": "object",
  "required": ["objective", "persona", "message_angles", "style_family", "cta_type", "safety_rules", "reasoning"],
  "properties": {
    "objective": {
      "type": "string",
      "enum": ["seeding", "conversion", "awareness", "engagement"],
      "description": "Confirmed marketing objective (may refine from input)"
    },
    "persona": {
      "type": "string",
      "description": "Target audience persona description in Chinese",
      "minLength": 10,
      "maxLength": 200,
      "examples": ["22-28岁都市通勤女性，注重护肤成分，偏好高性价比产品"]
    },
    "message_angles": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["angle", "hook_type", "rationale"],
        "properties": {
          "angle": {
            "type": "string",
            "description": "Creative angle description in Chinese",
            "minLength": 5,
            "maxLength": 100
          },
          "hook_type": {
            "type": "string",
            "enum": ["personal_story", "ingredient_focus", "problem_solution", "social_proof", "listicle", "question_hook"],
            "description": "Hook archetype for the title/opening"
          },
          "rationale": {
            "type": "string",
            "description": "Why this angle was chosen — references performance data or trend signals",
            "maxLength": 200
          }
        }
      },
      "minItems": 2,
      "maxItems": 5,
      "description": "Distinct creative angles to generate variants against"
    },
    "style_family": {
      "type": "string",
      "enum": ["治愈系插画", "轻漫画分镜", "可爱Q版生活场景", "手账贴纸风", "极简软萌插画"],
      "description": "Selected cartoon style family for the visual agent"
    },
    "cta_type": {
      "type": "string",
      "enum": ["收藏", "关注", "评论", "私信", "购买链接"],
      "description": "Primary call-to-action type"
    },
    "safety_rules": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1,
      "description": "Compliance guardrails specific to this generation run, in Chinese",
      "examples": [["不得使用绝对化用语（最好、第一）", "不得承诺具体效果", "不得引用未经验证的数据"]]
    },
    "tone_direction": {
      "type": "string",
      "enum": ["warm", "playful", "professional", "casual", "luxury"],
      "description": "Recommended tone for the Note Writer"
    },
    "selling_points_priority": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Selling points ordered by strategic priority for this run"
    },
    "reasoning": {
      "type": "string",
      "description": "Brief explanation of strategy choices — references input data and trade-offs",
      "minLength": 50,
      "maxLength": 500
    }
  }
}
```

### 2.3 Validation Rules

| Rule | Enforcement |
|---|---|
| `message_angles` must contain 2-5 distinct angles | Schema validation (minItems/maxItems) |
| Each angle must have a unique `hook_type` unless explicitly justified | Post-validation business rule |
| `safety_rules` must include at least one rule derived from `merchant_rules.banned_claims` | Post-validation business rule |
| `selling_points_priority` must include all items from `merchant_rules.required_claims` | Post-validation business rule |
| `style_family` must be from the defined enum | Schema validation |
| `persona` must be written in Chinese | Post-validation language check |

---

## 3. XiaoHongShu Note Writer Prompt Contract

**Prompt family:** `xhs_note_writer_v1`
**Agent role:** `xhs_note_writer`
**Upstream artifact:** `StrategyPlan`
**Downstream artifact:** `NoteContentSet`

The Note Writer generates platform-native XiaoHongShu copy: titles, bodies, first comments, hashtags, and cover text overlays. Output must feel native to the platform — not generic ad copy.

### 3.1 Input Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "NoteWriterInput",
  "type": "object",
  "required": ["product", "strategy", "merchant_rules", "xhs_native_rules"],
  "properties": {
    "product": {
      "type": "object",
      "required": ["name", "category", "description", "key_selling_points"],
      "properties": {
        "name": {
          "type": "string",
          "description": "Product display name"
        },
        "category": {
          "type": "string",
          "description": "Product category"
        },
        "description": {
          "type": "string",
          "description": "Full product description"
        },
        "key_selling_points": {
          "type": "array",
          "items": { "type": "string" },
          "minItems": 1,
          "description": "Ordered list of selling points to cover"
        },
        "ingredients_highlights": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Key ingredients or materials to reference"
        },
        "price": {
          "type": ["string", "null"],
          "description": "Product price (include only if strategy permits)"
        }
      }
    },
    "strategy": {
      "type": "object",
      "required": ["objective", "persona", "message_angles", "cta_type", "safety_rules"],
      "description": "Direct output from the Strategy Planner",
      "properties": {
        "objective": {
          "type": "string",
          "enum": ["seeding", "conversion", "awareness", "engagement"]
        },
        "persona": {
          "type": "string",
          "description": "Target audience description in Chinese"
        },
        "message_angles": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "angle": { "type": "string" },
              "hook_type": { "type": "string" }
            }
          }
        },
        "style_family": { "type": "string" },
        "cta_type": { "type": "string" },
        "safety_rules": {
          "type": "array",
          "items": { "type": "string" }
        },
        "tone_direction": { "type": "string" },
        "selling_points_priority": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "asset_context": {
      "type": "object",
      "description": "Available visual assets for text-image coordination",
      "properties": {
        "available_images": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "asset_id": { "type": "string" },
              "type": { "type": "string", "enum": ["packshot", "cutout", "logo", "hero"] },
              "description": { "type": "string" }
            }
          }
        },
        "cover_style_direction": {
          "type": "string",
          "description": "Visual style hint from strategy for text-cover coordination"
        }
      }
    },
    "merchant_rules": {
      "type": "object",
      "required": ["tone_preset"],
      "properties": {
        "tone_preset": { "type": "string" },
        "banned_words": {
          "type": "array",
          "items": { "type": "string" },
          "default": []
        },
        "required_claims": {
          "type": "array",
          "items": { "type": "string" },
          "default": []
        }
      }
    },
    "xhs_native_rules": {
      "type": "object",
      "required": ["max_title_length", "max_body_length", "hashtag_count_min", "hashtag_count_max"],
      "description": "XiaoHongShu platform formatting constraints",
      "properties": {
        "max_title_length": {
          "type": "integer",
          "default": 20,
          "description": "Maximum title length in characters"
        },
        "max_body_length": {
          "type": "integer",
          "default": 1000,
          "description": "Maximum body length in characters"
        },
        "hashtag_count_min": {
          "type": "integer",
          "default": 3,
          "description": "Minimum number of hashtags"
        },
        "hashtag_count_max": {
          "type": "integer",
          "default": 8,
          "description": "Maximum number of hashtags"
        },
        "emoji_allowed": {
          "type": "boolean",
          "default": true
        },
        "first_comment_max_length": {
          "type": "integer",
          "default": 500
        }
      }
    },
    "persona_context": {
      "type": ["object", "null"],
      "description": "Optional persona overlay — injected as Layer 1 system prefix",
      "properties": {
        "communication_style": { "type": "string" },
        "decision_style": { "type": "string" },
        "tone_rules": { "type": "array", "items": { "type": "string" } },
        "platform_vocabulary": { "type": "array", "items": { "type": "string" } },
        "emoji_density": { "type": "string", "enum": ["none", "sparse", "moderate", "heavy"] }
      }
    }
  }
}
```

### 3.2 Output Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "NoteWriterOutput",
  "type": "object",
  "required": ["title_variants", "body_variants", "first_comment", "hashtags", "cover_text_suggestions", "cta_text"],
  "properties": {
    "title_variants": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["text", "hook_type", "char_count"],
        "properties": {
          "text": {
            "type": "string",
            "maxLength": 20,
            "description": "Title text (≤20 Chinese characters)"
          },
          "hook_type": {
            "type": "string",
            "enum": ["curiosity", "benefit", "social_proof", "urgency", "question", "personal_story"],
            "description": "Hook archetype used in this title"
          },
          "char_count": {
            "type": "integer",
            "maximum": 20,
            "description": "Actual character count for validation"
          },
          "angle_ref": {
            "type": "string",
            "description": "Which message_angle this title corresponds to"
          }
        }
      },
      "minItems": 2,
      "maxItems": 6,
      "description": "At least 2 title variants per generation"
    },
    "body_variants": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["text", "tone", "word_count", "selling_points_covered"],
        "properties": {
          "text": {
            "type": "string",
            "maxLength": 1000,
            "description": "Full note body text (≤1000 Chinese characters)"
          },
          "tone": {
            "type": "string",
            "enum": ["warm", "playful", "professional", "casual"],
            "description": "Actual tone realized in this variant"
          },
          "word_count": {
            "type": "integer",
            "maximum": 1000,
            "description": "Actual character count"
          },
          "selling_points_covered": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Which required selling points are present in this body"
          },
          "structure": {
            "type": "string",
            "enum": ["hook_story_cta", "problem_solution", "listicle", "personal_diary", "comparison"],
            "description": "Note structure archetype used"
          },
          "angle_ref": {
            "type": "string",
            "description": "Which message_angle this body corresponds to"
          }
        }
      },
      "minItems": 1,
      "maxItems": 5,
      "description": "Body text variants"
    },
    "first_comment": {
      "type": "object",
      "required": ["text", "purpose"],
      "properties": {
        "text": {
          "type": "string",
          "maxLength": 500,
          "description": "Engaging first comment text in Chinese"
        },
        "purpose": {
          "type": "string",
          "enum": ["engagement_hook", "additional_info", "cta_reinforcement", "social_proof"],
          "description": "Strategic purpose of the first comment"
        }
      }
    },
    "hashtags": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^#.+",
        "description": "Hashtag including the # prefix"
      },
      "minItems": 3,
      "maxItems": 8,
      "description": "Hashtags ordered by relevance (mix of popular and niche)"
    },
    "cover_text_suggestions": {
      "type": "array",
      "items": {
        "type": "string",
        "maxLength": 30,
        "description": "Short text for cover image overlay (≤30 characters)"
      },
      "minItems": 1,
      "maxItems": 3,
      "description": "Cover text overlay suggestions for the visual agent"
    },
    "cta_text": {
      "type": "string",
      "maxLength": 50,
      "description": "Call-to-action text aligned with strategy.cta_type"
    }
  }
}
```

### 3.3 Validation Rules

| Rule | Enforcement |
|---|---|
| Every `title_variants[].text` must be ≤ 20 characters | Schema validation (maxLength) |
| Every `body_variants[].text` must be ≤ 1000 characters | Schema validation (maxLength) |
| `hashtags` count must be within [3, 8] | Schema validation (minItems/maxItems) |
| All items in `merchant_rules.required_claims` must appear in at least one `body_variants[].selling_points_covered` | Post-validation business rule |
| No item in `merchant_rules.banned_words` may appear in any text output | Post-validation banned-word scan |
| `first_comment.text` must not repeat the body verbatim | Post-validation deduplication check |
| All hashtags must start with `#` | Schema validation (pattern) |
| At least one title must use the `hook_type` specified in the strategy | Post-validation alignment check |

### 3.4 XiaoHongShu Native Writing Guidelines

These guidelines are embedded in the role system prompt (Layer 2) and are non-negotiable regardless of persona:

1. **No ad-speak.** Content must read like an authentic user post, not a brand advertisement.
2. **Line breaks for readability.** Use short paragraphs (2-3 sentences max) separated by blank lines.
3. **Hook-first structure.** The opening line must stop the scroll — question, bold claim, or relatable scenario.
4. **Emoji as punctuation.** Use emoji to break up text and add personality, not as decoration.
5. **Platform-native vocabulary.** Use terms like 种草, 安利, 姐妹们, 真的会谢 naturally — never forced.
6. **Soft CTA.** End with a question or invitation, not a hard sell.

---

## 4. Cartoon Visual Agent Prompt Contract

**Prompt family:** `cartoon_visual_v1`
**Agent role:** `cartoon_visual_designer`
**Upstream artifact:** `StrategyPlan`
**Downstream artifact:** `VisualAssetSet`

The Cartoon Visual Agent produces visual scene briefs, composition directives, and image generation prompts. It coordinates cartoon/illustration contexts around real product photography.

### 4.1 Input Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CartoonVisualInput",
  "type": "object",
  "required": ["product", "strategy", "visual_rules", "composition_rules"],
  "properties": {
    "product": {
      "type": "object",
      "required": ["name", "category"],
      "properties": {
        "name": {
          "type": "string",
          "description": "Product display name"
        },
        "category": {
          "type": "string",
          "description": "Product category"
        },
        "reference_asset_ids": {
          "type": "array",
          "items": { "type": "string" },
          "description": "IDs of approved product assets (packshots, cutouts) available for compositing"
        },
        "reference_asset_descriptions": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "asset_id": { "type": "string" },
              "type": { "type": "string", "enum": ["packshot", "cutout", "logo", "packaging_ref"] },
              "description": { "type": "string" },
              "dimensions": { "type": "string", "examples": ["800x1200"] }
            }
          },
          "description": "Metadata about available product assets"
        }
      }
    },
    "strategy": {
      "type": "object",
      "required": ["style_family", "persona", "message_angles"],
      "properties": {
        "style_family": {
          "type": "string",
          "enum": ["治愈系插画", "轻漫画分镜", "可爱Q版生活场景", "手账贴纸风", "极简软萌插画"],
          "description": "Visual style family from Strategy Planner"
        },
        "persona": {
          "type": "string",
          "description": "Target audience description for visual context"
        },
        "message_angles": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "angle": { "type": "string" },
              "hook_type": { "type": "string" }
            }
          },
          "description": "Creative angles to visualize"
        },
        "tone_direction": {
          "type": "string",
          "description": "Overall tone for visual mood alignment"
        }
      }
    },
    "visual_rules": {
      "type": "object",
      "required": ["preserve_product", "product_must_be_recognizable", "style_family"],
      "description": "Hard constraints on visual generation",
      "properties": {
        "preserve_product": {
          "type": "boolean",
          "const": true,
          "description": "Real product photography must NEVER be AI-altered or stylized"
        },
        "product_must_be_recognizable": {
          "type": "boolean",
          "const": true,
          "description": "Product must be clearly identifiable in the final image"
        },
        "style_family": {
          "type": "string",
          "enum": ["治愈系插画", "轻漫画分镜", "可爱Q版生活场景", "手账贴纸风", "极简软萌插画"],
          "description": "Approved cartoon style families"
        },
        "max_text_overlay_area_pct": {
          "type": "integer",
          "maximum": 30,
          "default": 30,
          "description": "Maximum percentage of image area that may contain text overlay"
        },
        "prohibited_styles": {
          "type": "array",
          "items": { "type": "string" },
          "default": ["any copyrighted IP references", "realistic human faces", "competitor brand imagery"],
          "description": "Styles and elements that must NOT appear"
        },
        "color_palette_hint": {
          "type": ["string", "null"],
          "description": "Optional brand color palette guidance",
          "examples": ["soft pastels with #F5E6D3 dominant", "vibrant primary colors"]
        }
      }
    },
    "composition_rules": {
      "type": "object",
      "required": ["cover_ratio"],
      "properties": {
        "cover_ratio": {
          "type": "string",
          "enum": ["3:4", "1:1"],
          "default": "3:4",
          "description": "Cover image aspect ratio"
        },
        "carousel_ratio": {
          "type": "string",
          "enum": ["3:4", "1:1"],
          "default": "3:4",
          "description": "Carousel image aspect ratio"
        },
        "max_carousel_count": {
          "type": "integer",
          "minimum": 0,
          "maximum": 9,
          "default": 5,
          "description": "Maximum number of carousel images"
        }
      }
    },
    "persona_context": {
      "type": ["object", "null"],
      "description": "Optional persona overlay for aesthetic preferences",
      "properties": {
        "communication_style": { "type": "string" },
        "aesthetic_preference": { "type": "string" }
      }
    }
  }
}
```

### 4.2 Output Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CartoonVisualOutput",
  "type": "object",
  "required": ["cover_brief", "carousel_briefs"],
  "properties": {
    "cover_brief": {
      "type": "object",
      "required": ["scene_description", "product_placement", "style_notes", "text_overlay", "image_prompt"],
      "properties": {
        "scene_description": {
          "type": "string",
          "description": "Detailed scene description in natural language — what the viewer sees",
          "minLength": 50,
          "maxLength": 500,
          "examples": ["温暖的卧室场景，柔和的晨光从窗户洒入，床头柜上摆放着产品，周围点缀着可爱的卡通小花和星星装饰"]
        },
        "product_placement": {
          "type": "string",
          "description": "How the real product appears in the scene — position, scale, context",
          "examples": ["产品居中偏右，占画面约25%，自然放置在梳妆台上，周围有卡通装饰元素环绕"]
        },
        "style_notes": {
          "type": "string",
          "description": "Art direction notes for the image generator",
          "examples": ["治愈系插画风，柔和渐变背景，圆润线条，暖色调为主，避免锐利边缘"]
        },
        "text_overlay": {
          "type": "object",
          "required": ["text", "position"],
          "properties": {
            "text": {
              "type": "string",
              "maxLength": 30,
              "description": "Cover text (coordinated with Note Writer suggestions)"
            },
            "position": {
              "type": "string",
              "enum": ["top", "center", "bottom", "top-left", "top-right", "bottom-left", "bottom-right"],
              "description": "Text placement on the cover"
            },
            "font_style_hint": {
              "type": "string",
              "enum": ["rounded", "handwritten", "minimal", "bold"],
              "description": "Font style suggestion"
            }
          }
        },
        "image_prompt": {
          "type": "string",
          "description": "Complete image generation prompt for the diffusion model. Must include style family, scene elements, color palette, and composition directives. Must explicitly state that product photography is composited separately and not generated.",
          "minLength": 100,
          "maxLength": 1000
        },
        "negative_prompt": {
          "type": "string",
          "description": "Negative prompt for the diffusion model — elements to exclude",
          "examples": ["realistic human faces, copyrighted characters, text, watermark, blurry, low quality"]
        }
      }
    },
    "carousel_briefs": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["position", "scene_description", "product_placement", "style_notes", "image_prompt"],
        "properties": {
          "position": {
            "type": "integer",
            "minimum": 1,
            "description": "Carousel position (1 = first after cover)"
          },
          "scene_description": {
            "type": "string",
            "description": "Scene description for this carousel slide",
            "minLength": 30,
            "maxLength": 500
          },
          "product_placement": {
            "type": "string",
            "description": "Product placement for this slide"
          },
          "style_notes": {
            "type": "string",
            "description": "Style continuity notes (must stay consistent with cover)"
          },
          "purpose": {
            "type": "string",
            "enum": ["product_detail", "usage_scenario", "ingredient_highlight", "before_after", "social_proof", "cta"],
            "description": "Strategic purpose of this carousel slide"
          },
          "image_prompt": {
            "type": "string",
            "description": "Complete image generation prompt for this slide",
            "minLength": 100,
            "maxLength": 1000
          },
          "negative_prompt": {
            "type": "string"
          }
        }
      },
      "minItems": 0,
      "maxItems": 9,
      "description": "Carousel slide briefs (may be empty if cover-only note)"
    },
    "style_consistency_notes": {
      "type": "string",
      "description": "Notes to ensure visual consistency across cover and carousel",
      "examples": ["All slides use the same warm pastel palette (#F5E6D3, #E8C4A0, #FFE4E1). Consistent rounded line style. Product cutout treatment is identical across all frames."]
    }
  }
}
```

### 4.3 Validation Rules

| Rule | Enforcement |
|---|---|
| `cover_brief.image_prompt` must reference the style family from input | Post-validation keyword check |
| `cover_brief.image_prompt` must NOT contain instructions to generate the product | Post-validation content check |
| All `carousel_briefs[].position` values must be sequential starting from 1 | Post-validation sequence check |
| `carousel_briefs` count must not exceed `composition_rules.max_carousel_count` | Post-validation count check |
| No `image_prompt` may reference copyrighted IP, real celebrity names, or competitor brands | Post-validation safety scan |
| `text_overlay.text` must be ≤ 30 characters | Schema validation (maxLength) |
| Style notes across all briefs must reference the same style family | Post-validation consistency check |

### 4.4 Product Fidelity Rules

These rules are embedded in the role system prompt and are **non-negotiable**:

1. **Real product photography is NEVER AI-generated.** The product image comes from approved assets in the Asset Registry.
2. **Product cutouts are composited onto the illustrated scene.** The cartoon/illustration is the background context; the product is a separate layer.
3. **Product proportions must be preserved.** No stretching, warping, or stylizing the product image.
4. **The image_prompt describes the scene AROUND the product**, not the product itself.
5. **Every image_prompt must include an explicit exclusion:** "Do not generate or alter the product — product photography will be composited separately."

---

## 5. Compliance Agent Prompt Contract

**Prompt family:** `compliance_reviewer_v1`
**Agent role:** `compliance_reviewer`
**Upstream artifacts:** `NoteContentSet` + `VisualAssetSet`
**Downstream artifact:** `ComplianceReport`

The Compliance Agent evaluates all generated content against regulatory rules (《广告法》), platform policies, merchant-specific banned words, and product-fidelity constraints. This is the safety gate — its decisions are final and cannot be overridden by persona.

### 5.1 Input Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ComplianceReviewerInput",
  "type": "object",
  "required": ["note_package", "merchant_rules", "policy_rules", "product"],
  "properties": {
    "note_package": {
      "type": "object",
      "required": ["titles", "bodies", "first_comment", "hashtags", "cover_text"],
      "description": "Assembled note content to review",
      "properties": {
        "titles": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["text", "hook_type"],
            "properties": {
              "text": { "type": "string" },
              "hook_type": { "type": "string" },
              "variant_id": { "type": "string" }
            }
          }
        },
        "bodies": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["text"],
            "properties": {
              "text": { "type": "string" },
              "tone": { "type": "string" },
              "variant_id": { "type": "string" }
            }
          }
        },
        "first_comment": {
          "type": "object",
          "properties": {
            "text": { "type": "string" }
          }
        },
        "hashtags": {
          "type": "array",
          "items": { "type": "string" }
        },
        "cover_text": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Text overlays on cover and carousel images"
        },
        "image_briefs": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "image_prompt": { "type": "string" },
              "style_notes": { "type": "string" },
              "product_fidelity_preserved": { "type": "boolean" }
            }
          },
          "description": "Visual briefs for image content compliance review"
        }
      }
    },
    "merchant_rules": {
      "type": "object",
      "required": ["banned_words"],
      "properties": {
        "banned_words": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Merchant-specific banned word list"
        },
        "banned_claims": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Claims explicitly banned by merchant"
        },
        "compliance_level": {
          "type": "string",
          "enum": ["strict", "standard", "relaxed"],
          "default": "standard",
          "description": "Strictness level — affects warning/fail thresholds"
        },
        "required_disclaimers": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Disclaimers that must appear if certain claims are made"
        }
      }
    },
    "policy_rules": {
      "type": "object",
      "required": ["global_rules"],
      "description": "Platform and regulatory compliance rules",
      "properties": {
        "global_rules": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["rule_id", "rule_type", "description"],
            "properties": {
              "rule_id": { "type": "string" },
              "rule_type": {
                "type": "string",
                "enum": ["banned_word", "required_word", "forbidden_claim", "category_restriction", "style_restriction", "max_overlay"]
              },
              "description": { "type": "string" },
              "payload": { "type": "object" }
            }
          },
          "description": "Platform-wide compliance rules"
        },
        "category_rules": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "rule_id": { "type": "string" },
              "category": { "type": "string" },
              "rule_type": { "type": "string" },
              "description": { "type": "string" },
              "payload": { "type": "object" }
            }
          },
          "description": "Category-specific rules (e.g., cosmetics cannot claim 'whitening' without certification)"
        }
      }
    },
    "product": {
      "type": "object",
      "required": ["category"],
      "properties": {
        "category": {
          "type": "string",
          "description": "Product category for rule matching"
        },
        "verified_claims": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Claims that have supporting evidence and are approved"
        },
        "certifications": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Product certifications (国妆特字, FDA, etc.)"
        }
      }
    }
  }
}
```

### 5.2 Output Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ComplianceReviewerOutput",
  "type": "object",
  "required": ["status", "issues", "confidence"],
  "properties": {
    "status": {
      "type": "string",
      "enum": ["passed", "failed", "review_needed"],
      "description": "Overall compliance verdict"
    },
    "issues": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["severity", "rule_type", "location", "detail", "suggestion"],
        "properties": {
          "severity": {
            "type": "string",
            "enum": ["critical", "warning", "info"],
            "description": "critical = auto-fail, warning = flag for review, info = advisory only"
          },
          "rule_type": {
            "type": "string",
            "enum": ["banned_word", "unsupported_claim", "hard_sell", "style_risk", "product_fidelity", "category_violation", "format_violation", "merchant_custom"],
            "description": "Type of compliance rule violated"
          },
          "location": {
            "type": "string",
            "enum": ["title", "body", "first_comment", "hashtag", "cover_text", "image_prompt", "image_style"],
            "description": "Where in the note package the issue was found"
          },
          "detail": {
            "type": "string",
            "description": "Specific description of the violation in Chinese",
            "examples": ["标题包含绝对化用语\"最好\"，违反《广告法》第九条"]
          },
          "suggestion": {
            "type": "string",
            "description": "Actionable remediation suggestion in Chinese",
            "examples": ["将\"最好的保湿精华\"改为\"深层保湿精华\""]
          },
          "matched_text": {
            "type": ["string", "null"],
            "description": "The exact text that triggered the violation"
          },
          "rule_id": {
            "type": ["string", "null"],
            "description": "Reference to the specific policy rule ID"
          }
        }
      },
      "description": "List of compliance issues found (empty array = clean pass)"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Model confidence in the overall assessment (0.0-1.0)"
    },
    "summary": {
      "type": "string",
      "description": "Human-readable compliance summary in Chinese for the merchant review UI",
      "maxLength": 500
    },
    "check_breakdown": {
      "type": "object",
      "description": "Per-check-type results for granular reporting",
      "properties": {
        "banned_words": { "type": "string", "enum": ["pass", "fail", "warning"] },
        "unsupported_claims": { "type": "string", "enum": ["pass", "fail", "warning"] },
        "hard_sell_risk": { "type": "string", "enum": ["pass", "fail", "warning"] },
        "style_risk": { "type": "string", "enum": ["pass", "fail", "warning"] },
        "product_fidelity": { "type": "string", "enum": ["pass", "fail", "warning"] },
        "category_rules": { "type": "string", "enum": ["pass", "fail", "warning"] },
        "format_compliance": { "type": "string", "enum": ["pass", "fail", "warning"] }
      }
    }
  }
}
```

### 5.3 Verdict Logic

| Condition | Status |
|---|---|
| Zero issues | `passed` |
| Any issue with `severity: "critical"` | `failed` |
| Any issue with `severity: "warning"` but no criticals | `review_needed` |
| Only `severity: "info"` issues | `passed` |

### 5.4 Compliance Check Categories

| Check Type | Description | Severity if Violated |
|---|---|---|
| `banned_word` | 《广告法》Article 9 superlatives (最好, 第一, 国家级), merchant-specific banned words | `critical` |
| `unsupported_claim` | Claims not in `product.verified_claims` (e.g., "美白" without 国妆特字) | `critical` for health/efficacy claims; `warning` for soft claims |
| `hard_sell` | Aggressive sales language violating XiaoHongShu community guidelines | `warning` |
| `style_risk` | Copyrighted IP references, celebrity likeness, trademark misuse in image prompts | `critical` |
| `product_fidelity` | `product_fidelity_preserved` is false, or image prompt attempts to generate the product | `critical` |
| `category_violation` | Category-specific regulatory rules (cosmetics, food, health supplements) | `critical` |
| `format_violation` | Title > 20 chars, body > 1000 chars, hashtag count out of range | `warning` |
| `merchant_custom` | Merchant-specific banned words or claims | Configurable per merchant |

### 5.5 Persona Influence Boundary

The Compliance Agent's persona may influence:
- How issues are **explained** to the merchant (formal vs. friendly language)
- How suggestions are **phrased**

The Compliance Agent's persona MUST NOT influence:
- Whether an issue is flagged
- The severity level of an issue
- The pass/fail/review_needed verdict
- Which rules are applied

---

## 6. Ranking Agent Prompt Contract

**Prompt family:** `ranking_analyst_v1`
**Agent role:** `ranking_analyst`
**Upstream artifact:** `ComplianceReport` (+ full creative set)
**Downstream artifact:** `RankingResult`

The Ranking Agent scores compliant creative variants across multiple quality dimensions and surfaces the highest-potential candidates.

### 6.1 Input Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RankingAnalystInput",
  "type": "object",
  "required": ["candidates"],
  "properties": {
    "candidates": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["variant_id", "title", "body", "visual_brief", "compliance_result"],
        "properties": {
          "variant_id": {
            "type": "string",
            "description": "Unique variant identifier"
          },
          "title": {
            "type": "object",
            "properties": {
              "text": { "type": "string" },
              "hook_type": { "type": "string" },
              "char_count": { "type": "integer" }
            }
          },
          "body": {
            "type": "object",
            "properties": {
              "text": { "type": "string" },
              "tone": { "type": "string" },
              "word_count": { "type": "integer" },
              "selling_points_covered": { "type": "array", "items": { "type": "string" } }
            }
          },
          "visual_brief": {
            "type": "object",
            "properties": {
              "style_family": { "type": "string" },
              "scene_description": { "type": "string" },
              "composition_type": { "type": "string" }
            }
          },
          "compliance_result": {
            "type": "object",
            "properties": {
              "status": { "type": "string", "enum": ["passed", "review_needed"] },
              "issue_count": { "type": "integer" },
              "confidence": { "type": "number" }
            }
          },
          "hashtags": {
            "type": "array",
            "items": { "type": "string" }
          },
          "first_comment": { "type": "string" }
        }
      },
      "minItems": 1,
      "description": "Compliance-passing (or review_needed) creative variants to rank"
    },
    "historical_performance": {
      "type": "object",
      "description": "Performance signals from Analytics Service",
      "properties": {
        "winning_patterns": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "pattern_type": { "type": "string", "enum": ["hook_type", "tone", "style_family", "structure", "cta_type"] },
              "pattern_value": { "type": "string" },
              "avg_engagement_rate": { "type": "number" },
              "avg_save_rate": { "type": "number" },
              "sample_size": { "type": "integer" }
            }
          },
          "description": "Content patterns that historically perform well"
        },
        "fatigued_patterns": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "pattern_type": { "type": "string" },
              "pattern_value": { "type": "string" },
              "fatigue_score": { "type": "number", "minimum": 0, "maximum": 1 },
              "engagement_decline_pct": { "type": "number" }
            }
          },
          "description": "Content patterns showing audience fatigue"
        }
      }
    },
    "merchant_preferences": {
      "type": "object",
      "description": "Merchant's stated preferences and priorities",
      "properties": {
        "preferred_tones": { "type": "array", "items": { "type": "string" } },
        "preferred_hook_types": { "type": "array", "items": { "type": "string" } },
        "priority_objective": { "type": "string" },
        "brand_voice_keywords": { "type": "array", "items": { "type": "string" } }
      }
    },
    "strategy_context": {
      "type": "object",
      "description": "Strategy plan for objective alignment scoring",
      "properties": {
        "objective": { "type": "string" },
        "persona": { "type": "string" },
        "required_selling_points": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

### 6.2 Output Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RankingAnalystOutput",
  "type": "object",
  "required": ["ranked_candidates"],
  "properties": {
    "ranked_candidates": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["note_package_id", "score", "score_breakdown", "recommendation"],
        "properties": {
          "note_package_id": {
            "type": "string",
            "description": "Variant identifier matching input candidates"
          },
          "score": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Composite ranking score (0.0-1.0)"
          },
          "score_breakdown": {
            "type": "object",
            "required": ["title_quality", "visual_quality", "merchant_fit", "objective_fit", "compliance_confidence", "novelty_score", "fatigue_avoidance"],
            "properties": {
              "title_quality": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Title hook effectiveness, clarity, and platform nativeness"
              },
              "visual_quality": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Visual brief quality — scene coherence, product placement, style execution"
              },
              "merchant_fit": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Alignment with merchant brand voice and preferences"
              },
              "objective_fit": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "How well the variant serves the stated marketing objective"
              },
              "compliance_confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Confidence in compliance clearance (from ComplianceReport)"
              },
              "novelty_score": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "How fresh/original the angle is relative to recent output"
              },
              "fatigue_avoidance": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Inverse of fatigue signal — higher means the angle is not fatigued"
              }
            }
          },
          "recommendation": {
            "type": "string",
            "enum": ["publish", "review", "revise", "discard"],
            "description": "Actionable recommendation for this variant"
          },
          "rationale": {
            "type": "string",
            "description": "Human-readable explanation of the ranking in Chinese",
            "maxLength": 300
          },
          "strengths": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Key strengths of this variant"
          },
          "weaknesses": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Key weaknesses or areas for improvement"
          }
        }
      },
      "description": "Candidates sorted by composite score descending"
    },
    "ranking_summary": {
      "type": "string",
      "description": "Overall ranking summary for the merchant dashboard, in Chinese",
      "maxLength": 500
    },
    "fatigue_warnings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "variant_id": { "type": "string" },
          "fatigued_dimension": { "type": "string" },
          "recommendation": { "type": "string" }
        }
      },
      "description": "Variants with fatigue concerns"
    }
  }
}
```

### 6.3 Scoring Weights

Default scoring weights (adjustable by the Learning Agent over time):

| Dimension | Default Weight | Description |
|---|---|---|
| `title_quality` | 0.20 | Title hook effectiveness |
| `visual_quality` | 0.15 | Visual brief coherence |
| `merchant_fit` | 0.15 | Brand voice alignment |
| `objective_fit` | 0.20 | Marketing objective fit |
| `compliance_confidence` | 0.10 | Compliance clearance confidence |
| `novelty_score` | 0.10 | Freshness relative to recent content |
| `fatigue_avoidance` | 0.10 | Avoidance of fatigued patterns |

### 6.4 Recommendation Thresholds

| Composite Score | Recommendation |
|---|---|
| ≥ 0.80 | `publish` — high confidence, ready for minimal review |
| 0.60 – 0.79 | `review` — solid but needs merchant attention |
| 0.40 – 0.59 | `revise` — has potential but needs changes |
| < 0.40 | `discard` — not worth publishing or revising |

---

## 7. Founder Copilot Prompt Contract

**Prompt family:** `founder_copilot_v1`
**Agent role:** `founder_copilot`
**Upstream:** Free-text merchant input
**Downstream artifact:** `StructuredJobRequest`

The Founder Copilot is the conversational interface for merchants. It translates natural-language requests (in Chinese) into structured generation jobs. It has the highest persona influence of any agent.

### 7.1 Input Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FounderCopilotInput",
  "type": "object",
  "required": ["user_message", "merchant_context"],
  "properties": {
    "user_message": {
      "type": "string",
      "description": "Natural language request from the merchant, typically in Chinese",
      "examples": [
        "帮我给新出的玻尿酸精华做一组种草笔记",
        "最近流量下滑了，能不能换个风格试试",
        "做3条聚光投放的素材，要突出成分"
      ]
    },
    "merchant_context": {
      "type": "object",
      "required": ["merchant_id", "merchant_name"],
      "properties": {
        "merchant_id": {
          "type": "string",
          "description": "Merchant tenant ID"
        },
        "merchant_name": {
          "type": "string",
          "description": "Merchant display name"
        },
        "industry": {
          "type": "string",
          "description": "Merchant industry vertical"
        },
        "products": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "product_id": { "type": "string" },
              "name": { "type": "string" },
              "category": { "type": "string" },
              "status": { "type": "string", "enum": ["active", "paused", "archived"] }
            }
          },
          "description": "Active products in the merchant's catalog"
        },
        "recent_activity": {
          "type": "object",
          "properties": {
            "last_generation_date": { "type": ["string", "null"], "format": "date" },
            "last_generation_product": { "type": ["string", "null"] },
            "active_campaigns": { "type": "integer", "default": 0 },
            "pending_reviews": { "type": "integer", "default": 0 }
          },
          "description": "Recent merchant activity for context-aware responses"
        },
        "available_channels": {
          "type": "array",
          "items": { "type": "string", "enum": ["organic", "聚光", "蒲公英"] },
          "description": "Distribution channels available to this merchant"
        },
        "merchant_rules_summary": {
          "type": "object",
          "properties": {
            "tone_preset": { "type": "string" },
            "compliance_level": { "type": "string" }
          },
          "description": "Summary of merchant rules for conversation context"
        }
      }
    },
    "conversation_history": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["role", "content"],
        "properties": {
          "role": {
            "type": "string",
            "enum": ["user", "assistant"],
            "description": "Message sender"
          },
          "content": {
            "type": "string",
            "description": "Message content"
          },
          "timestamp": {
            "type": "string",
            "format": "date-time"
          }
        }
      },
      "description": "Prior conversation turns for multi-turn context"
    },
    "persona_context": {
      "type": ["object", "null"],
      "description": "Optional persona overlay — highest influence on this agent",
      "properties": {
        "communication_style": { "type": "string" },
        "decision_style": { "type": "string" },
        "tone_rules": { "type": "array", "items": { "type": "string" } },
        "greeting_style": { "type": "string" },
        "empathy_level": { "type": "string", "enum": ["low", "medium", "high"] }
      }
    }
  }
}
```

### 7.2 Output Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FounderCopilotOutput",
  "type": "object",
  "required": ["intent", "response_to_user", "needs_clarification"],
  "properties": {
    "intent": {
      "type": "string",
      "enum": ["generate_note", "modify_existing", "ask_question", "manage_assets", "export", "view_analytics", "other"],
      "description": "Parsed intent from the merchant's message"
    },
    "structured_job": {
      "type": ["object", "null"],
      "description": "Structured job request — populated when intent is 'generate_note' and all required info is resolved",
      "properties": {
        "product_id": {
          "type": "string",
          "description": "Resolved product ID from merchant context"
        },
        "objective": {
          "type": "string",
          "enum": ["seeding", "conversion", "awareness", "engagement"],
          "description": "Resolved marketing objective"
        },
        "persona": {
          "type": ["string", "null"],
          "description": "Target audience if specified by merchant"
        },
        "style_preference": {
          "type": ["string", "null"],
          "description": "Visual style preference if mentioned"
        },
        "tone_preference": {
          "type": ["string", "null"],
          "description": "Tone preference if mentioned"
        },
        "channels": {
          "type": "array",
          "items": { "type": "string", "enum": ["organic", "聚光", "蒲公英"] },
          "description": "Target distribution channels"
        },
        "special_instructions": {
          "type": ["string", "null"],
          "description": "Any special instructions extracted from the merchant's message"
        },
        "urgency": {
          "type": "string",
          "enum": ["normal", "urgent"],
          "default": "normal",
          "description": "Inferred urgency level"
        },
        "variant_count": {
          "type": "integer",
          "minimum": 1,
          "maximum": 20,
          "default": 3,
          "description": "Number of variants requested"
        }
      }
    },
    "response_to_user": {
      "type": "string",
      "description": "Natural language response to the merchant in Chinese. Must be helpful, concise, and on-brand with the persona.",
      "minLength": 10,
      "maxLength": 1000
    },
    "needs_clarification": {
      "type": "boolean",
      "description": "Whether the copilot needs more information before proceeding"
    },
    "clarification_questions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["question", "field"],
        "properties": {
          "question": {
            "type": "string",
            "description": "Clarification question in Chinese"
          },
          "field": {
            "type": "string",
            "description": "Which structured_job field this question resolves",
            "enum": ["product_id", "objective", "persona", "style_preference", "channels", "special_instructions", "variant_count"]
          },
          "options": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Suggested options for the merchant to choose from (in Chinese)"
          }
        }
      },
      "description": "Questions to ask when needs_clarification is true"
    },
    "context_surfaced": {
      "type": ["string", "null"],
      "description": "Relevant context proactively surfaced to the merchant (e.g., 'You last generated for this product 5 days ago')"
    }
  }
}
```

### 7.3 Intent Resolution Rules

| Trigger Phrases (Chinese) | Resolved Intent |
|---|---|
| 生成/做/写 + 笔记/内容/素材 | `generate_note` |
| 修改/改一下/调整 + 之前的/上次的 | `modify_existing` |
| 怎么/如何/什么是 | `ask_question` |
| 上传/素材/图片/资产 | `manage_assets` |
| 导出/下载/发布 | `export` |
| 数据/表现/流量/效果 | `view_analytics` |

### 7.4 Clarification Strategy

When the merchant's message is ambiguous, the Copilot must ask clarifying questions rather than guessing. Questions should be:

1. **Minimal** — ask only what's needed, one question at a time when possible.
2. **Contextual** — reference the merchant's catalog and history to offer smart defaults.
3. **Option-driven** — provide selectable options rather than open-ended questions.

---

## 8. Prompt Versioning Rules

All prompts are managed through the `prompt_versions` table in PostgreSQL.

### 8.1 Database Schema Reference

```sql
CREATE TABLE prompt_versions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_family VARCHAR(128)  NOT NULL,
    version       INT           NOT NULL,
    template      TEXT          NOT NULL,
    variables     JSONB         NOT NULL DEFAULT '{}'::jsonb,
    status        prompt_status NOT NULL DEFAULT 'draft',
    created_at    TIMESTAMPTZ   NOT NULL DEFAULT now(),
    CONSTRAINT prompt_versions_family_version UNIQUE (prompt_family, version)
);
```

### 8.2 Versioning Lifecycle

```
draft ──► active ──► deprecated
  │                      │
  └──────── (delete) ◄───┘ (only if never used in production)
```

| Status | Description |
|---|---|
| `draft` | Under development. Not used in production pipelines. Can be tested in staging. |
| `active` | The current production version for this prompt family. **At most one active version per family.** |
| `deprecated` | Previously active. Retained for audit trail and replay. Cannot be used for new generation runs. |

### 8.3 Version Resolution

At generation time, the Agent Runtime resolves the prompt version:

1. Query `prompt_versions` for the agent's `prompt_family` where `status = 'active'`.
2. If no active version exists, fail the generation with a clear error.
3. Load the template and bind variables from the pipeline artifacts.
4. Record the `prompt_version` ID in the generation lineage.

### 8.4 Template Variable Binding

Templates use Jinja2 syntax. The `variables` JSONB column declares the expected variable schema:

```json
{
  "product_name": { "type": "string", "required": true },
  "product_category": { "type": "string", "required": true },
  "product_description": { "type": "string", "required": true },
  "selling_points": { "type": "array", "required": true },
  "tone_preset": { "type": "string", "required": false, "default": "种草安利" },
  "banned_words": { "type": "array", "required": false, "default": [] },
  "persona_prefix": { "type": "string", "required": false, "default": "" }
}
```

### 8.5 Version Immutability Rules

1. An `active` version is **immutable** once any generation run references it.
2. To modify a prompt, create a new version (increment the version number), test in staging, then promote to active.
3. The previously active version is automatically transitioned to `deprecated`.
4. Deprecated versions are retained indefinitely for audit and replay.
5. Draft versions may be freely edited until promoted.

### 8.6 Prompt Family Naming Convention

```
{agent_role}_{purpose}_v{major}

Examples:
  strategy_planner_v1
  xhs_note_writer_v1
  cartoon_visual_v1
  compliance_reviewer_v1
  ranking_analyst_v1
  founder_copilot_v1
```

---

## 9. Persona Injection Pattern

Persona context is injected as a system-level instruction prefix (Layer 1 in the prompt composition stack). It shapes the agent's tone and style without altering the role's operational responsibilities or output schema.

### 9.1 Injection Template

```
你是一位{{ communication_style }}的{{ role_display_name }}。
{{ description }}。
你的沟通风格是{{ tone_rules | join('。') }}。
{% if forbidden_behaviors %}
你绝对不能：{{ forbidden_behaviors | join('；') }}。
{% endif %}
{% if cultural_context and cultural_context.platform_vocabulary %}
你自然使用以下平台用语：{{ cultural_context.platform_vocabulary | join('、') }}。
{% endif %}
```

### 9.2 Injection Example

For persona `persona_genz_voice_v2` bound to `xhs_note_writer`:

```
你是一位像真实小红书用户分享个人发现一样写作的小红书文案专家。
Writes like a Gen-Z XiaoHongShu native — casual, emoji-rich, authentic, trend-aware。
你的沟通风格是Use 种草安利 tone with 闺蜜 energy。Open with a hook question or exclamation。Include 2-4 emoji per paragraph。Use line breaks liberally for readability。Reference real usage scenarios (通勤, 约会, 上课)。End body text with a soft CTA or question。
你绝对不能：Never use formal business language (请您, 尊敬的)；Never write in paragraph-essay format；Never make medical or efficacy claims；Never reference competitor brands by name；Never use English words when a Chinese internet slang equivalent exists。
你自然使用以下平台用语：种草、安利、姐妹们、yyds、绝绝子、真的会谢、救命、一整个爱住。
```

### 9.3 Injection Rules

| Rule | Description |
|---|---|
| **Persona prefix comes before role prompt** | Layer 1 (persona) is prepended to Layer 2 (role). Role instructions take precedence on any conflict. |
| **Persona is optional** | If no persona is bound (`persona_id: null`), Layer 1 is empty. The role prompt runs standalone. |
| **Persona never defines output schema** | The output JSON structure is defined exclusively in the role prompt (Layer 2). |
| **Persona forbidden_behaviors are enforced post-generation** | After LLM output, the Agent Runtime checks for violations of `forbidden_behaviors` and retries if found. |
| **Persona snapshot is frozen at resolution time** | The `ResolvedTeamComposition` artifact contains a frozen persona snapshot. Mid-pipeline persona edits do not affect in-flight generations. |

### 9.4 Per-Role Persona Influence Levels

| Agent Role | Persona Influence | What Persona Shapes |
|---|---|---|
| `founder_copilot` | **High** | Greeting style, question style, empathy level, vocabulary, formality |
| `strategy_planner` | **Medium** | Strategic framing, risk appetite in angle selection, explanation style |
| `xhs_note_writer` | **High** | Tone, vocabulary, emoji density, sentence structure, hook preferences |
| `cartoon_visual_designer` | **Medium** | Aesthetic preferences, color mood, composition style |
| `compliance_reviewer` | **Low** | Explanation style only — never pass/fail decisions |
| `ranking_analyst` | **Low** | Rationale explanation style — never scoring |
| `ops_exporter` | **None** | Purely operational — no persona |
| `learning_analyst` | **Low** | Insight communication style |

---

## 10. Structured Output Validation

Every LLM response is validated against the output schema before being accepted into the pipeline.

### 10.1 Validation Pipeline

```
LLM Response (raw text)
    │
    ▼
Step 1: JSON Parse ── fail ──► Retry with "respond in valid JSON only" suffix
    │
    ▼
Step 2: Schema Validation ── fail ──► Retry with specific missing/invalid fields listed
    │
    ▼
Step 3: Business Rule Checks ── fail ──► Retry with specific rule violation details
    │
    ▼
Step 4: Persona Constraint Checks ── fail ──► Retry with forbidden behavior flagged
    │
    ▼
Accept ── wrap into typed pipeline artifact
```

### 10.2 Retry Policy

| Retry | Strategy |
|---|---|
| Retry 1 | Re-send the same prompt with an appended instruction: "Your previous response was not valid JSON. Respond ONLY with a JSON object matching the required schema." |
| Retry 2 | Include the specific validation errors in the prompt: "Your response failed validation: {error_details}. Fix these issues and respond again." |
| Retry 3 | Simplify the prompt — reduce context, increase schema emphasis, lower temperature. |
| After 3 failures | Mark the generation task as `failed`. Log the error. Alert the observability system. |

### 10.3 Validation Error Types

| Error Type | Description | Retry Strategy |
|---|---|---|
| `json_parse_error` | Response is not valid JSON | Append JSON-only instruction |
| `schema_validation_error` | Missing required fields, wrong types, enum violations | List specific failures |
| `business_rule_violation` | Banned words present, required claims missing, etc. | Describe the specific violation |
| `persona_constraint_violation` | Forbidden behavior detected in output | Flag the specific behavior |
| `length_violation` | Character count exceeds platform limits | Specify the limit and current count |

---

## 11. Prompt Template Examples

### 11.1 Strategy Planner System Prompt (Layer 2)

```
你是GenPos平台的策略规划师。你的职责是根据产品信息、商家规则和市场数据，制定小红书创意生成策略。

## 你的输入
你将收到以下信息：
- 产品信息（名称、类别、描述、营销目标）
- 商家规则（语气预设、禁用词、必须卖点、禁止声称）
- 效果数据（近期高表现角度、疲劳角度、趋势话题）

## 你的输出要求
你必须返回严格符合以下JSON格式的策略方案。不要输出任何JSON之外的内容。

{
  "objective": "seeding|conversion|awareness|engagement",
  "persona": "目标受众描述（中文，10-200字）",
  "message_angles": [
    {
      "angle": "创意角度描述",
      "hook_type": "personal_story|ingredient_focus|problem_solution|social_proof|listicle|question_hook",
      "rationale": "选择理由"
    }
  ],
  "style_family": "治愈系插画|轻漫画分镜|可爱Q版生活场景|手账贴纸风|极简软萌插画",
  "cta_type": "收藏|关注|评论|私信|购买链接",
  "safety_rules": ["合规规则1", "合规规则2"],
  "tone_direction": "warm|playful|professional|casual|luxury",
  "selling_points_priority": ["卖点1", "卖点2"],
  "reasoning": "策略选择的简要解释（50-500字）"
}

## 策略制定规则
1. message_angles 必须包含2-5个不重复的角度
2. 必须参考效果数据，避免疲劳角度（fatigue_score > 0.7）
3. safety_rules 必须包含所有 banned_claims 对应的规则
4. selling_points_priority 必须包含所有 required_claims
5. 所有中文内容必须符合小红书平台风格
```

### 11.2 Note Writer System Prompt (Layer 2)

```
你是GenPos平台的小红书文案专家。你的职责是根据策略方案和产品信息，撰写原生感十足的小红书笔记内容。

## 平台规则（不可违反）
- 标题不超过20个中文字符
- 正文不超过1000个中文字符
- 话题标签3-8个
- 内容必须像真实用户分享，不能像广告

## 你的输出要求
你必须返回严格符合以下JSON格式的内容。不要输出任何JSON之外的内容。

{
  "title_variants": [
    { "text": "标题文字", "hook_type": "curiosity|benefit|social_proof|urgency|question|personal_story", "char_count": 15, "angle_ref": "角度引用" }
  ],
  "body_variants": [
    { "text": "完整正文", "tone": "warm|playful|professional|casual", "word_count": 300, "selling_points_covered": ["卖点1"], "structure": "hook_story_cta|problem_solution|listicle|personal_diary|comparison", "angle_ref": "角度引用" }
  ],
  "first_comment": { "text": "首评文字", "purpose": "engagement_hook|additional_info|cta_reinforcement|social_proof" },
  "hashtags": ["#话题1", "#话题2", "#话题3"],
  "cover_text_suggestions": ["封面文字1", "封面文字2"],
  "cta_text": "行动号召文字"
}

## 写作规则
1. 标题必须有钩子：提问、利益承诺、社交证明、或个人故事开头
2. 正文结构：开头钩子 → 场景/痛点 → 产品介绍 → 使用感受 → 软性CTA
3. 段落简短（2-3句），多用换行
4. 自然使用小红书平台用语，不要生硬堆砌
5. 首评要引导互动，不要重复正文内容
6. 话题标签混合热门和垂直标签
```

---

## Appendix A: Schema Cross-Reference

| Contract | Input Source | Output Destination | Validation Model |
|---|---|---|---|
| Strategy Planner | `StructuredJobRequest` + product truth + analytics | `StrategyPlan` | Pydantic `StrategyPlannerOutput` |
| Note Writer | `StrategyPlan` + product truth + merchant rules | `NoteContentSet` | Pydantic `NoteWriterOutput` |
| Cartoon Visual | `StrategyPlan` + approved assets + brand visuals | `VisualAssetSet` | Pydantic `CartoonVisualOutput` |
| Compliance | `NoteContentSet` + `VisualAssetSet` + rules | `ComplianceReport` | Pydantic `ComplianceReviewerOutput` |
| Ranking | Compliant variants + performance history | `RankingResult` | Pydantic `RankingAnalystOutput` |
| Founder Copilot | Free-text + merchant context | `StructuredJobRequest` | Pydantic `FounderCopilotOutput` |

## Appendix B: Prompt Version Tracking Dimensions

Every LLM call in production records the following in the generation lineage:

| Dimension | Source | Example |
|---|---|---|
| `prompt_family` | `prompt_versions.prompt_family` | `xhs_note_writer_v1` |
| `prompt_version` | `prompt_versions.version` | `3` |
| `prompt_id` | `prompt_versions.id` | `uuid` |
| `model_version` | Generation Service config | `qwen-max-2025-12` |
| `persona_id` | `ResolvedTeamComposition` | `persona_genz_voice_v2` |
| `persona_version` | Persona snapshot | `2.0.0` |
| `input_hash` | SHA-256 of assembled prompt | `a1b2c3...` |
| `output_hash` | SHA-256 of validated output | `d4e5f6...` |
| `token_usage` | LLM response metadata | `{input: 2340, output: 512}` |
| `latency_ms` | Timer | `3200` |
| `retry_count` | Retry tracker | `0` |
| `validation_result` | Validation pipeline | `pass` |

## Appendix C: Related Documents

| Document | Path | Relationship |
|---|---|---|
| Architecture | `docs/architecture/ARCHITECTURE.md` | System architecture; § 8 defines Agent Runtime |
| Agent Team Spec | `docs/architecture/AGENT_TEAM_SPEC.md` | Agent roles, pipeline, typed artifacts (§ 12) |
| ERD | `docs/architecture/ERD.sql` | Database schema; `prompt_versions` and `policy_rules` tables |
| OpenAPI | `docs/api/openapi.yaml` | API contracts for generation endpoints |
| PRD | `docs/prd/PRD.md` | Product requirements; § 8 defines AI agent features |
