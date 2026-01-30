"""
PPK Document Factory - Core Module
==================================
Core functionality including database, caching, workers, and performance monitoring.
"""

from .config import *
from .database import DatabaseManager, get_db_manager

# Cache System
from .cache import (
    CacheEntry,
    CacheStats,
    DataCache,
    cached,
    cache_invalidate,
    get_cache,
    clear_cache,
    cache_stats,
)

# Cached Database
from .cached_database import (
    CachedDatabaseManager,
    get_cached_db_manager,
)

# Workers
from .workers import (
    WorkerSignals,
    BaseWorker,
    FunctionWorker,
    ProgressFunctionWorker,
    BatchWorker,
    SequentialWorker,
    run_in_background,
    run_with_progress,
    background_task,
    async_slot,
    WorkerPool,
)

# Performance Monitoring
from .performance import (
    PerformanceStats,
    MemoryStats,
    PerformanceMonitor,
    MemoryMonitor,
    measure_time,
    measure_memory,
    measure_performance,
    log_slow,
    get_monitor,
    enable_monitoring,
    disable_monitoring,
    print_stats,
)

__all__ = [
    # Database
    'DatabaseManager',
    'get_db_manager',

    # Cached Database
    'CachedDatabaseManager',
    'get_cached_db_manager',

    # Cache
    'CacheEntry',
    'CacheStats',
    'DataCache',
    'cached',
    'cache_invalidate',
    'get_cache',
    'clear_cache',
    'cache_stats',

    # Workers
    'WorkerSignals',
    'BaseWorker',
    'FunctionWorker',
    'ProgressFunctionWorker',
    'BatchWorker',
    'SequentialWorker',
    'run_in_background',
    'run_with_progress',
    'background_task',
    'async_slot',
    'WorkerPool',

    # Performance
    'PerformanceStats',
    'MemoryStats',
    'PerformanceMonitor',
    'MemoryMonitor',
    'measure_time',
    'measure_memory',
    'measure_performance',
    'log_slow',
    'get_monitor',
    'enable_monitoring',
    'disable_monitoring',
    'print_stats',
]
