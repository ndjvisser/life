"""Legacy life_stats app retained for migration references.

The concrete LifeStat models have been moved to the consolidated
``life_dashboard.stats`` app. This placeholder module intentionally omits
model definitions so Django's migration graph can continue to resolve
historical dependencies without recreating deprecated tables.
"""

__all__ = []
