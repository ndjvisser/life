# Business Logic Blueprint (BLB)

This document links the Product Requirements Document (PRD) to concrete business value and the technical architecture. It clarifies why each capability matters, what logic turns it into value, and where that logic will live in the codebase.

## Purpose

Provide a single source of truth for how product features (PRD) map to monetizable or strategic outcomes and the domain-driven modules in the code. It is the handshake between product, engineering, and stakeholders.

## Value-Logic-Tech Traceability Matrix

| PRD Feature | Business Value | Core Logic (Domain Service) | Owning Django App / Context |
|-------------|----------------|------------------------------|----------------------------|
| Core Stats (Strength...Charisma) | Engages users via gamification → ↑ retention | StatService.adjust_stat, LevelService.check_level_up | stats |
| Life Stats (Health/Wealth/Relationships) | Shows holistic progress → differentiates product | LifeStatService.update_metric, trend calculators | stats |
| **Real-World Integrations** | **Auto-updates = stickiness → 10x user value** | **IntegrationService.sync_external_data, ValidationService** | **stats** |
| Quests & Habits | Drives repeat behavior → daily active usage | QuestService.transition_state, HabitScheduler | quests |
| **Quest Auto-Completion** | **Reduces friction → higher completion rates** | **ProductivityIntegration.sync_tasks, QuestService.auto_complete** | **quests** |
| Skills & XP | Power-user pathway → subscription upsell tier | SkillService.level_skill, XP accrual handlers | skills |
| Achievements & Badges | Social proof & virality → shareable milestones | AchievementEngine.evaluate_rules, event listeners | achievements |
| Journal | Captures insights → data moats for coaching features | JournalService.create_entry, NLP tags (future) | journals |
| **Insight Generation** | **AI coaching features → premium tier differentiation** | **InsightEngine.analyze_patterns, TrendDetectionService** | **journals** |
| **Predictive Analytics** | **Proactive guidance → enterprise/coaching value** | **PredictionService.forecast_trends, BalanceScorer** | **dashboard** |
| Overviews & Dashboards | Premium analytics → tiered pricing | OverviewAggregator.build_snapshot() | dashboard |

## Domain Event Flow (Enhanced Example)

### Manual Quest Completion Flow
1. User completes quest → `QuestCompleted` event
2. `AchievementEngine` listens → grants badge if criteria met
3. `StatService` awards XP to relevant CoreStat
4. `OverviewAggregator` recalculates dashboards (asynchronous task) → front-end refresh via WebSocket

### Automated Integration Flow
1. External API sync → `ExternalDataReceived` event
2. `ValidationService` validates and transforms data → `StatUpdated` event
3. `TrendDetectionService` analyzes patterns → `InsightGenerated` event
4. `PredictionService` forecasts trends → `RecommendationCreated` event
5. `NotificationService` alerts user to insights and recommendations

### Cross-Context Intelligence Flow
1. Multiple stat updates → `PatternDetected` event
2. `BalanceScorer` evaluates life balance → `BalanceShiftDetected` event
3. `InsightEngine` generates actionable recommendations → `ActionableInsightCreated` event
4. `CoachingService` suggests quest/habit adjustments → `PersonalizedRecommendation` event

## Key Business Rules

### Level-Up Rule
When any CoreStat crosses a multiple of 100 XP, call `LevelService` → generate `LevelUp` event → notify user; increase difficulty curve by 10%.

### Habit Streak Rule
If a habit is maintained ≥ 21 consecutive days, mark as streak and award bonus XP.

### Financial Goal Completion
When savings ≥ goal target, trigger `WealthAchievement` badge and suggest next tier goal.

### Skill Mastery Progression
Skills require exponentially more XP per level (base * 1.1^level) to maintain engagement curve.

### Achievement Unlock Cascades
Unlocking certain achievements automatically creates new, higher-tier challenges to maintain progression.

## Success Metrics (Logic-Driven)

| Metric | Logic Source | Target |
|--------|--------------|--------|
| Daily Active Users (DAU) | QuestService check-ins + habit completions + auto-updates | 45% of MAU |
| Retention Day-30 | Users with ≥ 1 CoreStat update / week (manual or auto) | ≥ 30% |
| **Integration Adoption** | **Users with ≥ 1 active external integration** | **40% of active users** |
| **Data Richness** | **% of stats auto-updated vs manual entry** | **≥ 60% automated** |
| Feature Adoption | Users who configured ≥ 1 Life Goal | 60% of new users |
| Engagement Depth | Users with ≥ 3 active habits | 25% of DAU |
| **Insight Engagement** | **Users who act on generated insights** | **35% of insight recipients** |
| **Predictive Accuracy** | **% of predictions that prove correct** | **≥ 70% accuracy** |
| Premium Conversion | Users accessing overview dashboards + insights | 15% conversion rate |
| **Life OS Stickiness** | **Users active across ≥ 3 life areas simultaneously** | **20% of DAU** |

## Revenue Logic Mapping

### Freemium Tier Limits
- Max 3 active quests
- Basic stats tracking (manual entry only)
- Limited journal entries (10/month)
- No external integrations
- Basic dashboard only

### Premium Tier Unlocks ($9.99/month)
- Unlimited quests and habits
- Full life stats tracking with trends
- **External integrations (health, finance, productivity)**
- **AI-generated insights and recommendations**
- Advanced achievement system
- Unlimited journaling with insights
- Data export capabilities
- **Predictive analytics and balance scoring**

### Life OS Pro Tier ($29.99/month)
- **Advanced AI coaching and personalized recommendations**
- **Custom integration development**
- **API access for personal automation**
- **Advanced trend analysis and forecasting**
- **Personal data scientist features**
- Priority support and feature requests

### Enterprise/Coaching Tier ($99.99/month)
- Team/family sharing and collaboration
- **Multi-user analytics and reporting**
- **Coaching dashboard for mentors/trainers**
- **White-label customization options**
- **Advanced API access and webhooks**
- Custom achievement and gamification systems

## Technical Anchors

- **Hexagonal Ports & Adapters** around each context
- **Domain Events** via Django signals → future-proof for Kafka
- **Service Layer** resides in `application/` package within each app
- **Pure Domain Models** in `domain/` (no Django imports)
- **Repository Pattern** for data access abstraction
- **Anti-Corruption Layers** at context boundaries

## Business Rule Implementation Patterns

### Rule Engine Pattern
```python
# achievements/domain/rules.py
class AchievementRule:
    def evaluate(self, user_context: UserContext) -> bool:
        pass

class StreakMasterRule(AchievementRule):
    def evaluate(self, user_context: UserContext) -> bool:
        return user_context.longest_habit_streak >= 30
```

### Event-Driven Business Logic
```python
# stats/application/handlers.py
@handles(QuestCompleted)
def award_quest_xp(event: QuestCompleted):
    stat_service.add_experience(
        event.user_id,
        event.experience_reward
    )
```

### Value Object Validation
```python
# stats/domain/value_objects.py
class StatValue:
    def __init__(self, value: int):
        if not 1 <= value <= 100:
            raise ValueError("Stat must be between 1-100")
        self._value = value
```

## Integration Value Multipliers

### Network Effects
- **Health Integration**: Each connected device/app increases user stickiness by 15%
- **Wealth Integration**: Financial data connectivity drives 3x higher premium conversion
- **Productivity Integration**: Task sync reduces quest abandonment by 40%
- **Social Integration**: Relationship tracking creates unique differentiation vs competitors

### Data Compound Value
- **Month 1**: Basic tracking and manual entry
- **Month 3**: Pattern recognition and basic insights
- **Month 6**: Predictive recommendations and balance optimization
- **Month 12**: Personal AI coach with deep behavioral understanding
- **Year 2+**: Life optimization system with decade+ of personal data

### Platform Evolution Path
1. **Personal Tool** (0-1K users): Individual life tracking and gamification
2. **Life OS** (1K-10K users): Integrated personal command center with AI insights
3. **Coaching Platform** (10K-100K users): Enable coaches/mentors to guide users
4. **Life Intelligence Network** (100K+ users): Anonymized insights and benchmarking

This blueprint ensures that every feature has clear business justification, technical implementation guidance, and strategic value multiplication, making the codebase both valuable and maintainable while building toward a 10x platform vision.
