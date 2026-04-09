# Phase 2 — Multi-merchant work (deferred)

**Status:** Intentionally **not** implemented for the current milestone. The product is run as a **single-merchant** deployment: JWT `sub` (and optional explicit `merchant_id` when provided) scopes all tenant data.

**Purpose of this note:** When multi-tenant Phase 2 requirements return, use this as a checklist and map back to code and backlog items.

---

## What already works in single-merchant mode

| Area | Behavior |
|------|-----------|
| Auth | Dev JWT embeds `sub` and `merchant_id` (same UUID). |
| API | `docs` pattern in `apps/api/src/core/tenant.py`: omit `merchant_id` on many routes → defaults to `sub`. |
| Daily batch | `POST /generate/daily/run-all` iterates merchants with active products; with one merchant it is a single logical tenant. |
| Temporal | Per-merchant workflow ids `daily-batch-{merchant_id}-{shanghai_date}`; schedule `DailyRunAllScheduledWorkflow` runs sync batches for **all** merchants in DB. |

---

## Deferred backlog themes (Phase 2 / adjacent)

1. **True multi-merchant UX**  
   - Merchant switcher, org/tenant admin, cross-merchant **deny** tests in CI.  
   - Remove or gate assumptions in copy (“单商户实例” in `apps/web/src/components/layout/header.tsx`).

2. **`POST /generate/daily/run-all` policy**  
   - Today: cron/system triggers batch for **every** merchant with active products.  
   - Future: per-tenant schedule preferences (BL-201), opt-out flags, rate limits **across** tenants, admin-only “run all”.

3. **RBAC beyond “one token = one merchant”**  
   - BL-304 mentions `owner` / `admin` for asset approval; generation paths today trust any valid JWT for that merchant.  
   - Add roles to JWT + dependency checks when multi-merchant admin surfaces exist.

4. **Temporal / cron**  
   - Single schedule for all merchants is fine at small scale; later: per-tenant schedules or queue sharding.

5. **Idempotency & fairness**  
   - Global concurrency caps (BL-205), priority of on-demand over daily for **shared** API quotas.

---

## Code anchors (search from repo root)

- Tenant resolution: `apps/api/src/core/tenant.py`
- Daily run-all + cron secret: `apps/api/src/api/v1/endpoints/generation.py`
- Scheduled workflow: `apps/api/src/temporal/workflows/daily_run_all.py`, `activities/daily_run_all.py`
- Schedule registration: `apps/api/scripts/register_daily_schedule.py`
- Web API calls (no redundant `merchant_id`): `apps/web/src/app/(workspace)/*/page.tsx`

---

## Related backlog IDs

- **BL-201** — Daily scheduler (full multi-tenant productization still open).  
- **BL-205** — Batch parallelism / global limits.  
- **BL-207** — Queue archival rules across days (verify with multi-merchant data).

When picking this up, re-read **`docs/BUILD_BACKLOG.md` § Phase 2** and **`production_plan.md` § Phase 2**.
