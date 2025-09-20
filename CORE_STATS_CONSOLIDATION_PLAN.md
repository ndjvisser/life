# Core Stats Consolidation Migration Plan

## Problem
The codebase has duplicate CoreStat models:
- **Old**: `life_dashboard.core_stats.models.CoreStat` (table: `core_stats_corestat`)
- **New**: `life_dashboard.stats.infrastructure.models.CoreStatModel` (table: `stats_corestat`)

This creates data inconsistency and violates the single source of truth principle.

## Solution: Consolidation Strategy

We will consolidate to the new `stats.CoreStatModel` and remove the old `core_stats` app.

## Migration Steps

### Phase 1: Comprehensive Data Migration (SAFE - Reversible)

1. **Run consolidated migration**: `stats.0002_consolidate_stats_models`
   - Creates new models: `CoreStatModel`, `LifeStatModel`, `LifeStatCategoryModel`, `StatHistoryModel`
   - **Includes comprehensive data migration**:
     - Migrates `core_stats.CoreStat` → `stats.CoreStatModel`
     - Migrates `life_stats.LifeStat` → `stats.LifeStatModel` (converts FK to CharField for category)
     - Migrates `life_stats.LifeStatCategory` → `stats.LifeStatCategoryModel`
     - Handles schema differences (Float→Decimal, FK→CharField)
     - Preserves all user relationships and timestamps
     - Avoids duplicates with existence checks
   - **Fully Reversible**: Includes backward migration functions
   - Status: ✅ Enhanced with data migration

3. **Update code references**:
   - ✅ Updated `dashboard/views.py` to use `CoreStatModel` with `core_stats` relation
   - ✅ Updated `shared/queries.py` to use `core_stats` relation
   - ✅ Fixed `related_name` to maintain backward compatibility
   - Status: ✅ Complete

### Phase 2: Reference Updates (SAFE - Reversible)

4. **Run FK migration**: `stats.0004_remove_old_core_stats_references`
   - Updates any foreign key references (none found in current codebase)
   - **Reversible**: Can restore old FK references
   - Status: ✅ Created

### Phase 3: Cleanup (DESTRUCTIVE - Plan carefully)

5. **Run deprecation migrations**:
   - `core_stats.0002_deprecate_core_stats`: Drops old `CoreStat` model
   - `life_stats.0002_deprecate_life_stats`: Drops old `LifeStat` and `LifeStatCategory` models
   - Both verify data migration completion before dropping tables
   - **⚠️ DESTRUCTIVE**: Cannot be easily reversed
   - Status: ✅ Created for both apps

6. **Remove deprecated apps from INSTALLED_APPS**:
   ```python
   # In settings.py, remove these lines:
   "life_dashboard.core_stats",
   "life_dashboard.life_stats",
   ```

7. **Delete deprecated app directories**:
   ```bash
   rm -rf life_dashboard/core_stats/
   rm -rf life_dashboard/life_stats/
   ```

## Execution Commands

```bash
# Phase 1: Comprehensive Data Migration
python manage.py migrate stats 0002_consolidate_stats_models

# Verify data migration
python manage.py shell -c "
from life_dashboard.core_stats.models import CoreStat
from life_dashboard.life_stats.models import LifeStat, LifeStatCategory
from life_dashboard.stats.infrastructure.models import CoreStatModel, LifeStatModel, LifeStatCategoryModel
print(f'Old core stats: {CoreStat.objects.count()}')
print(f'New core stats: {CoreStatModel.objects.count()}')
print(f'Old life stats: {LifeStat.objects.count()}')
print(f'New life stats: {LifeStatModel.objects.count()}')
print(f'Old categories: {LifeStatCategory.objects.count()}')
print(f'New categories: {LifeStatCategoryModel.objects.count()}')
"

# Phase 2: Reference Updates
python manage.py migrate stats 0004_remove_old_core_stats_references

# Phase 3: Cleanup (DESTRUCTIVE)
python manage.py migrate core_stats 0002_deprecate_core_stats
python manage.py migrate life_stats 0002_deprecate_life_stats

# Manual cleanup
# 1. Remove deprecated apps from INSTALLED_APPS in settings.py
# 2. Delete deprecated app directories
```

## Rollback Plan

If issues occur, rollback in reverse order:

```bash
# Rollback cleanup (if not yet deleted)
python manage.py migrate core_stats 0001_initial

# Rollback reference updates
python manage.py migrate stats 0003_consolidate_core_stats_data

# Rollback data migration
python manage.py migrate stats 0002_consolidate_stats_models

# Restore old code references manually
```

## Verification Steps

After each phase:

1. **Verify data integrity**:
   ```python
   # Check record counts match
   old_count = CoreStat.objects.count()
   new_count = CoreStatModel.objects.count()
   assert old_count == new_count

   # Check data matches for sample user
   user = User.objects.first()
   old_stats = user.core_stats
   new_stats = user.consolidated_core_stats
   assert old_stats.strength == new_stats.strength
   # ... check all fields
   ```

2. **Test application functionality**:
   - Login and view dashboard
   - Update core stats
   - Verify stats display correctly
   - Check admin interface

3. **Run test suite**:
   ```bash
   python manage.py test
   ```

## Benefits After Consolidation

- ✅ Single source of truth for core stats
- ✅ Consistent with DDD architecture (stats context)
- ✅ Eliminates data duplication
- ✅ Cleaner codebase with fewer apps
- ✅ Proper domain boundaries

## Risk Mitigation

- **Data Loss Prevention**: All migrations are reversible until Phase 3
- **Referential Integrity**: FK updates preserve relationships
- **Testing**: Comprehensive verification at each step
- **Backup**: Take database backup before Phase 3
- **Gradual Rollout**: Can pause between phases if issues arise

## Related Files Modified

- ✅ `life_dashboard/dashboard/views.py` - Updated to use new model with core_stats relation
- ✅ `life_dashboard/shared/queries.py` - Updated to use core_stats relation
- ✅ `life_dashboard/stats/infrastructure/models.py` - Fixed related_name for backward compatibility
- ✅ Created migration files for safe data transfer
- 🔄 `life_dashboard/life_dashboard/settings.py` - Remove core_stats app (manual step)

## Status: Ready for Execution

All migration files created and code references updated. Ready to execute Phase 1.
