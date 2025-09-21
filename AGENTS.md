# AGENTS.md

## 🚀 Mission
LIFE is a **modular monolith Life OS** that gamifies health, wealth, and relationships.
Agents must 10x output by:
- Preserving **strict DDD boundaries**.
- Using **canonical domain events** for cross-context flow.
- Writing **pure Python business logic** in `domain/` (no Django imports).
- Always checking **Business Logic Blueprint (BLB)** for value alignment.

---

## ⚙️ Setup
```bash
# Install dev + prod deps
pip install -r requirements-dev.txt
pip install -r requirements.txt

# Run server
python manage.py runserver

# Migrations
python manage.py migrate

# Celery workers
celery -A life_dashboard worker -l info
celery -A life_dashboard beat -l info
```

---

## 🧭 Project Rules

### Architecture
- Modular monolith with bounded contexts:`stats/`, `quests/`, `skills/`,
  `achievements/`, `journals/`, `integrations/`, `analytics/`, `dashboard/`.
- Each context uses:
  ```
  domain/ → pure logic
  infrastructure/ → ORM, APIs
  application/ → services, orchestration
  interfaces/ → views, serializers, endpoints
  ```
- **No cross-context imports.** Use domain events.

### Domain Events
- Defined only in [Domain Events Catalog](.kiro/steering/domain-events-catalog.md).
- Schema must include: `event_id`, `timestamp`, `version`.
- Always raise events in services, never mutate cross-context state directly.

### Business Logic
- Map every PRD feature → Business Value → Domain Service → Context.
- If logic location unclear, default to **domain service** (pure Python).

---

## 🛠️ Common Commands
```bash
# Tests
pytest
behave features/
pytest --cov=life_dashboard

# Lint/format
ruff check .
ruff format .
pre-commit run --all-files

# Generate insights for user 1
python manage.py generate_insights --user-id=1
```

---

## ✅ Coding Standards
- **Python 3.10+**, **Django 5.1.1**.
- Type hints + `mypy --strict`.
- Ruff enforces formatting; no Black/Flake8.
- Functional patterns > OOP unless domain-driven.
- Repository pattern for persistence.
- Event-driven orchestration (no Django signals).
- Tests at all four levels:
  1. Domain (pure Python)
  2. Application (service orchestration)
  3. Integration (ORM/API)
  4. Feature (BDD with Behave)

---

## 🔒 Security & Privacy
- Implement **Privacy context** with consent management.
- All event handling must validate user consent before processing.
- Follow GDPR-style retention + minimization.

---

## 🧪 PR Rules
- Title: `[<context>] <short description>`
- CI must pass: `pytest`, `ruff check`, `mypy`.
- Add/modify tests for all new logic.
- Use domain events instead of direct service calls unless intra-context.

---

## 🌐 Integration Guidance
- Adapters for APIs (health, finance, productivity).
- Always wrap external APIs behind domain adapters.
- Validate + transform data before raising events.

---

## 📊 Value Alignment
Agents should optimize for metrics that drive adoption:
- ≥ 40% of active users with ≥ 1 integration
- ≥ 60% automated stat updates
- ≥ 70% prediction accuracy
- ≥ 35% insight engagement
- ≥ 20% DAU active across ≥ 3 life areas

---

## 🏗️ Implementation Flow
1. **Check requirements**.
2. **Find logic home** in BLB.
3. **Implement in domain service**.
4. **Raise canonical event**.
5. **Write tests** at appropriate level.
6. **Run lint + CI**.

---

## ⚡ Agent Shortcuts
- Use **make reset && make setup-sample-data** (coming soon).
- Use `pytest -k "<testname>"` for focused runs.
- Use `python manage.py export_user_data --user-id=<id>` to debug event flows.

---

## 📂 Key References
- [architecture.md](.kiro/steering/architecture.md) → DDD + modular rules
- [business-logic.md](.kiro/steering/business-logic.md) → BLB traceability
- [domain-events-catalog.md](.kiro/steering/domain-events-catalog.md) → canonical
  events
- [requirements.md](.kiro/specs/personal-life-dashboard/requirements.md) → acceptance criteria
- [design.md](.kiro/specs/personal-life-dashboard/design.md) → API + testing strategy
- [tasks.md](.kiro/specs/personal-life-dashboard/tasks.md) → implementation plan

---

👉 Treat **AGENTS.md as law**: if unclear, default to *domain service + event*.
This guarantees consistency, scalability, and 10x leverage across agents.
