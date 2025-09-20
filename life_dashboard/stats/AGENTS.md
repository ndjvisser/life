stats/AGENTS.md

Purpose: Enable agents to ship fast, correct, DDD-compliant code for the Stats context (Core RPG stats + Life Stats + trends). Treat this file as law inside life_dashboard/stats/.

0) Ground rules (non-negotiable)

Boundaries

No Django imports in stats/domain/**.

No cross-context imports (e.g., from quests/, achievements/, etc.). Use domain events.

Persistence goes via repositories in infrastructure/; orchestration lives in application/.

Events first

Cross-context effects are emitted as canonical events; never call other contexts directly.

Tests required

Domain → pure Python unit tests.

Application → service orchestration tests.

Interfaces → API/view tests.

BDD where flows matter (e.g., “CoreStat updated → Achievement unlock evaluated”).

Type safety

Add type hints everywhere; mypy --strict must pass.

Lint

ruff check . && ruff format . before commit.

1) Scope of the stats context

Core Stats: Strength, Endurance, Agility, Intelligence, Wisdom, Charisma; XP; Level.

Life Stats: Health / Wealth / Relationships with subcategories; units; history; trends.

Signals: Stat milestones, trend detection, balance inputs for analytics.

Not here: Achievements logic, Quests/Habits logic, User auth/profile (those are other contexts).

2) Directory contract
stats/
├─ domain/                  # Pure logic (NO Django)
│  ├─ entities.py           # CoreStat, LifeStat, StatHistory (domain models)
│  ├─ value_objects.py      # StatName, Category, Unit, StatValue(1..100), XP, Level
│  ├─ services.py           # StatService, LevelService, TrendService (pure)
│  ├─ repositories.py       # abstract: StatRepository, HistoryRepository
│  └─ events.py             # re-exports of canonical event dataclasses (or thin wrappers)
├─ application/             # Orchestration
│  ├─ services.py           # command/query services; emits events
│  ├─ handlers.py           # event handlers local to stats (if any)
│  └─ queries.py            # read-models / projections for UIs
├─ infrastructure/          # Django & I/O
│  ├─ models.py             # ORM models mirror domain (no business rules)
│  ├─ repositories.py       # DjangoStatRepository, DjangoHistoryRepository
│  └─ migrations/
└─ interfaces/              # IO edges
   ├─ api_views.py          # REST endpoints
   ├─ serializers.py        # Pydantic/DRF serializers (no rules)
   └─ urls.py


Prohibited in domain/: from django..., DB queries, HTTP clients, file IO, logging side-effects.

3) Canonical events (emit/read)

Emit from application/services.py after successful commands:

CoreStatUpdated(user_id, stat_name, previous_value, new_value, source, version="1.0.0")

LifeStatUpdated(user_id, category, subcategory, previous_value, new_value, unit, source, version="1.0.0")

StatMilestoneReached(user_id, stat_type, stat_name, milestone_value, milestone_type, version="1.0.0")

TrendDetected(user_id, stat_name, trend_type, confidence_score, duration_days, version="1.0.0")

When XP thresholds crossed: emit ExperienceAwarded(...) and, if level changes, LevelUp(...).

Never call Achievements/Quests services directly; they subscribe to these events elsewhere.

4) Fast paths (copy-paste recipes)
A) Update a Core Stat (and award XP)

Domain (domain/services.py)

class StatService:
    def adjust_core_stat(self, core: CoreStat, name: StatName, delta: int) -> CoreStat:
        updated = core.with_adjustment(name, delta)  # enforces range & rules
        xp = updated.xp_gain_for_adjustment(name, delta)
        return updated.add_xp(xp)


Application (application/services.py)

class StatCommands:
    def update_core_stat(self, user_id: int, stat_name: str, delta: int):
        core = self.repo.load_core(user_id)
        updated = self.domain.adjust_core_stat(core, StatName(stat_name), delta)
        self.repo.save_core(user_id, updated)

        self.events.publish(CoreStatUpdated(...))
        if updated.xp_gained > 0:
            self.events.publish(ExperienceAwarded(...))
        if updated.level_changed():
            self.events.publish(LevelUp(...))


Tests

Domain: range, XP curve, level function.

Application: event emission + repository interactions (mock repo).

B) Add a new Life Stat metric

Define subcategory + unit in domain/value_objects.py.

Extend LifeStat to validate (category, subcategory, unit) triples.

Add update_life_stat(...) in domain/services.py.

Map persistence in infrastructure/models.py (tables: LifeStat, StatHistory).

Emit LifeStatUpdated and append a StatHistory entry.

C) Trend detection hook

Keep detection pure in domain/services.py:

class TrendService:
    def detect(self, history: Sequence[HistoryPoint]) -> Optional[Trend]:
        # pure math: slope/seasonality/z-score; return Trend or None


Application layer loads history → runs TrendService.detect → emits TrendDetected if confidence ≥ threshold.

5) Repositories (contracts)
class StatRepository(Protocol):
    def load_core(self, user_id: int) -> CoreStat: ...
    def save_core(self, user_id: int, core: CoreStat) -> None: ...
    def load_life(self, user_id: int, category: Category) -> list[LifeStat]: ...
    def save_life(self, user_id: int, stat: LifeStat) -> None: ...

class HistoryRepository(Protocol):
    def append(self, user_id: int, key: str, value: Decimal, unit: str, ts: datetime) -> None: ...
    def range(self, user_id: int, key: str, days: int) -> list[HistoryPoint]: ...


Implementation: infrastructure/repositories.py using Django ORM. Keep transactions here; domain stays pure.

6) XP & Level rules (reference implementation)

XP curve: additive by action; configurable map in domain/value_objects.py.

Level: function of total XP. Keep curve in one place; domain unit tests must cover:

exact thresholds,

monotonicity,

no off-by-one at boundaries.

If touching curve/thresholds → snapshot tests for regression + emit a version bump in events if payload meaning changes.

7) Milestones & safeguards

Milestones are derived, never stored; compute from current value/history.

Guardrails:

StatValue range 1..100 (hard fail outside).

Units mandatory for Life Stats; store as canonical strings (e.g., "kg", "EUR", "bpm").

History writes must be idempotent for (user_id, key, timestamp) to survive retries.

Large imports: batch HistoryRepository.append (vectorised or bulk insert).

8) Interfaces (API surface)

Write endpoints only as thin adapters:

PUT /api/v1/stats/core/{user_id}
PUT /api/v1/stats/life/{user_id}
GET /api/v1/stats/trends/{user_id}?days=30


Validate input (serializers/Pydantic), call application services, return DTOs.

No business rules in views/serializers.

9) Performance & reliability targets

Domain operations: < 2 ms each (pure functions).

Trend queries (30 days): < 50 ms from cached read model; fallback < 200 ms.

Bulk history insert: 10k points < 2 s.

No cross-context DB FKs; communicate via events.

On failure: never drop user updates; queue and retry with back-off in infrastructure layer if needed.

10) Legacy migration notes

We are consolidating core_stats/ + life_stats/ into stats/.

New work must land in stats/ with DDD layout.

If touching legacy modules, create thin anti-corruption adapters that call the new application services.

Write a migration script that:

maps legacy tables → new schema,

re-computes history keys (category.subcategory.unit),

verifies counts & checksums,

is idempotent.

11) PR checklist (must pass)

 Domain logic added/changed has pure tests.

 Events emitted are canonical & versioned.

 mypy --strict clean; ruff check clean.

 No Django import in domain/**.

 Repositories mocked in application tests.

 API/view changes covered by tests.

 Performance notes: any O(N) → O(log N) or batch strategy considered.

 Docs: updated this file or inline README in changed folder if behaviour shifts.

12) Quick commands
# Run all tests for stats
pytest life_dashboard/stats -q
# Lint & type
ruff check . && mypy .
# Coverage (helpful during refactors)
pytest --cov=life_dashboard/stats


Default when unsure: implement in domain service → application orchestrates → emit events → persist via repository.
