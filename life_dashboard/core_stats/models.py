"""Legacy core_stats app kept for migration compatibility.

The original CoreStat model has been superseded by
``life_dashboard.stats.infrastructure.models.CoreStatModel`` and the tables
have been removed via migrations. This module intentionally defines no Django
models to avoid conflicts with the consolidated stats app while still allowing
historical migrations that reference ``core_stats`` to load.
"""

__all__ = []
