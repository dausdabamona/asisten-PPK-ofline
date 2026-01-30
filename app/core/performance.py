"""
PPK Document Factory - Performance Monitor
==========================================
Performance monitoring system for debugging and optimization.

Features:
- Timer-based performance tracking
- Statistics collection (avg, min, max, count)
- Memory monitoring
- Context managers and decorators
- Debug widget for visualization

Example Usage:
-------------
```python
from app.core.performance import (
    PerformanceMonitor, measure_time, measure_performance
)

# Get singleton monitor
monitor = PerformanceMonitor()

# Manual timing
timer_id = monitor.start_timer("database_query")
result = db.query()
duration = monitor.stop_timer(timer_id)

# Context manager
with measure_time("generate_document"):
    doc = generator.generate(template, data)

# Decorator
@measure_performance
def slow_operation():
    pass

# Print stats
for name, stats in monitor.get_stats().items():
    print(f"{name}: avg={stats.avg_time_ms:.2f}ms, calls={stats.call_count}")
```
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from functools import wraps
from contextlib import contextmanager
import threading
import time
import uuid
import logging
import os
import gc

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class PerformanceStats:
    """
    Statistics for a single operation.

    Attributes:
        operation_name: Name of the operation
        call_count: Number of times called
        total_time_ms: Total time spent
        avg_time_ms: Average time per call
        min_time_ms: Minimum time
        max_time_ms: Maximum time
        last_time_ms: Most recent time
    """
    operation_name: str
    call_count: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float('inf')
    max_time_ms: float = 0.0
    last_time_ms: float = 0.0

    @property
    def avg_time_ms(self) -> float:
        """Calculate average time."""
        if self.call_count == 0:
            return 0.0
        return self.total_time_ms / self.call_count

    def record(self, duration_ms: float) -> None:
        """Record a new timing."""
        self.call_count += 1
        self.total_time_ms += duration_ms
        self.last_time_ms = duration_ms
        self.min_time_ms = min(self.min_time_ms, duration_ms)
        self.max_time_ms = max(self.max_time_ms, duration_ms)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation": self.operation_name,
            "calls": self.call_count,
            "total_ms": round(self.total_time_ms, 2),
            "avg_ms": round(self.avg_time_ms, 2),
            "min_ms": round(self.min_time_ms, 2) if self.min_time_ms != float('inf') else 0,
            "max_ms": round(self.max_time_ms, 2),
            "last_ms": round(self.last_time_ms, 2),
        }


@dataclass
class MemoryStats:
    """
    Memory usage statistics.

    Attributes:
        rss_bytes: Resident Set Size (physical memory used)
        vms_bytes: Virtual Memory Size
        percent: Memory percentage
        available_bytes: Available system memory
    """
    rss_bytes: int = 0
    vms_bytes: int = 0
    percent: float = 0.0
    available_bytes: int = 0

    @property
    def rss_mb(self) -> float:
        """RSS in megabytes."""
        return self.rss_bytes / (1024 * 1024)

    @property
    def vms_mb(self) -> float:
        """VMS in megabytes."""
        return self.vms_bytes / (1024 * 1024)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rss_mb": round(self.rss_mb, 2),
            "vms_mb": round(self.vms_mb, 2),
            "percent": round(self.percent, 1),
        }


@dataclass
class Timer:
    """Active timer instance."""
    timer_id: str
    name: str
    start_time: float
    thread_id: int


# =============================================================================
# PERFORMANCE MONITOR
# =============================================================================


class PerformanceMonitor:
    """
    Singleton performance monitor for tracking operation timings.

    Provides timing, statistics, and memory monitoring capabilities.
    Disabled by default in production; enable for debugging.

    Example:
    --------
    ```python
    monitor = PerformanceMonitor()
    monitor.enable()

    # Start/stop timer
    timer_id = monitor.start_timer("my_operation")
    do_work()
    duration = monitor.stop_timer(timer_id)

    # Get statistics
    stats = monitor.get_stats()
    for name, stat in stats.items():
        print(f"{name}: {stat.avg_time_ms}ms average")
    ```
    """

    _instance: Optional['PerformanceMonitor'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'PerformanceMonitor':
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize monitor."""
        if self._initialized:
            return

        self._stats: Dict[str, PerformanceStats] = {}
        self._active_timers: Dict[str, Timer] = {}
        self._enabled = False
        self._data_lock = threading.RLock()
        self._initialized = True

        logger.debug("PerformanceMonitor initialized")

    # =========================================================================
    # ENABLE/DISABLE
    # =========================================================================

    def enable(self) -> None:
        """Enable performance monitoring."""
        self._enabled = True
        logger.info("Performance monitoring enabled")

    def disable(self) -> None:
        """Disable performance monitoring."""
        self._enabled = False
        logger.info("Performance monitoring disabled")

    @property
    def is_enabled(self) -> bool:
        """Check if monitoring is enabled."""
        return self._enabled

    # =========================================================================
    # TIMING
    # =========================================================================

    def start_timer(self, name: str) -> str:
        """
        Start a timer.

        Args:
            name: Name of the operation being timed

        Returns:
            Timer ID (use to stop timer)
        """
        if not self._enabled:
            return ""

        timer_id = str(uuid.uuid4())[:8]
        timer = Timer(
            timer_id=timer_id,
            name=name,
            start_time=time.perf_counter(),
            thread_id=threading.get_ident()
        )

        with self._data_lock:
            self._active_timers[timer_id] = timer

        return timer_id

    def stop_timer(self, timer_id: str) -> float:
        """
        Stop a timer and record the duration.

        Args:
            timer_id: Timer ID from start_timer()

        Returns:
            Duration in milliseconds
        """
        if not self._enabled or not timer_id:
            return 0.0

        end_time = time.perf_counter()

        with self._data_lock:
            timer = self._active_timers.pop(timer_id, None)
            if timer is None:
                return 0.0

            duration_ms = (end_time - timer.start_time) * 1000

            # Record stats
            if timer.name not in self._stats:
                self._stats[timer.name] = PerformanceStats(timer.name)

            self._stats[timer.name].record(duration_ms)

        logger.debug(f"Timer '{timer.name}': {duration_ms:.2f}ms")
        return duration_ms

    def record(self, name: str, duration_ms: float) -> None:
        """
        Directly record a timing (for external measurements).

        Args:
            name: Operation name
            duration_ms: Duration in milliseconds
        """
        if not self._enabled:
            return

        with self._data_lock:
            if name not in self._stats:
                self._stats[name] = PerformanceStats(name)
            self._stats[name].record(duration_ms)

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_stats(self, name: Optional[str] = None) -> Dict[str, PerformanceStats]:
        """
        Get performance statistics.

        Args:
            name: Specific operation name, or None for all

        Returns:
            Dictionary of operation name -> PerformanceStats
        """
        with self._data_lock:
            if name:
                stat = self._stats.get(name)
                return {name: stat} if stat else {}
            return self._stats.copy()

    def get_top_operations(self, n: int = 10, by: str = "avg") -> List[PerformanceStats]:
        """
        Get top N slowest operations.

        Args:
            n: Number of operations to return
            by: Sort key - "avg", "total", "max", or "count"

        Returns:
            List of PerformanceStats, sorted by specified key
        """
        with self._data_lock:
            stats_list = list(self._stats.values())

        if by == "avg":
            key = lambda s: s.avg_time_ms
        elif by == "total":
            key = lambda s: s.total_time_ms
        elif by == "max":
            key = lambda s: s.max_time_ms
        elif by == "count":
            key = lambda s: s.call_count
        else:
            key = lambda s: s.avg_time_ms

        return sorted(stats_list, key=key, reverse=True)[:n]

    def reset(self) -> None:
        """Reset all statistics."""
        with self._data_lock:
            self._stats.clear()
            self._active_timers.clear()
        logger.debug("Performance stats reset")

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all performance data.

        Returns:
            Dictionary with summary statistics
        """
        with self._data_lock:
            total_calls = sum(s.call_count for s in self._stats.values())
            total_time = sum(s.total_time_ms for s in self._stats.values())

            return {
                "operations_tracked": len(self._stats),
                "total_calls": total_calls,
                "total_time_ms": round(total_time, 2),
                "active_timers": len(self._active_timers),
                "top_5_avg": [
                    s.to_dict() for s in self.get_top_operations(5, "avg")
                ],
            }


# =============================================================================
# MEMORY MONITOR
# =============================================================================


class MemoryMonitor:
    """
    Monitor memory usage.

    Provides methods to check current memory usage and track growth.
    """

    _baseline: Optional[int] = None
    _checkpoints: Dict[str, int] = {}

    @classmethod
    def get_usage(cls) -> MemoryStats:
        """
        Get current memory usage.

        Returns:
            MemoryStats with current memory information
        """
        try:
            import psutil
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            mem_percent = process.memory_percent()

            return MemoryStats(
                rss_bytes=mem_info.rss,
                vms_bytes=mem_info.vms,
                percent=mem_percent,
            )
        except ImportError:
            # psutil not available, return empty stats
            return MemoryStats()

    @classmethod
    def set_baseline(cls) -> int:
        """
        Set current memory as baseline.

        Returns:
            Current RSS in bytes
        """
        stats = cls.get_usage()
        cls._baseline = stats.rss_bytes
        return cls._baseline

    @classmethod
    def get_growth(cls) -> int:
        """
        Get memory growth since baseline.

        Returns:
            Memory growth in bytes (negative if decreased)
        """
        if cls._baseline is None:
            return 0
        current = cls.get_usage().rss_bytes
        return current - cls._baseline

    @classmethod
    def checkpoint(cls, label: str) -> int:
        """
        Create a memory checkpoint.

        Args:
            label: Label for the checkpoint

        Returns:
            Current RSS in bytes
        """
        current = cls.get_usage().rss_bytes
        cls._checkpoints[label] = current
        return current

    @classmethod
    def get_growth_since(cls, label: str) -> int:
        """
        Get memory growth since a checkpoint.

        Args:
            label: Checkpoint label

        Returns:
            Growth in bytes since checkpoint
        """
        if label not in cls._checkpoints:
            return 0
        current = cls.get_usage().rss_bytes
        return current - cls._checkpoints[label]

    @classmethod
    def force_gc(cls) -> int:
        """
        Force garbage collection and return freed memory.

        Returns:
            Number of objects collected
        """
        before = cls.get_usage().rss_bytes
        collected = gc.collect()
        after = cls.get_usage().rss_bytes
        freed = before - after

        logger.debug(f"GC: collected {collected} objects, freed {freed} bytes")
        return collected


# =============================================================================
# CONTEXT MANAGERS
# =============================================================================


@contextmanager
def measure_time(name: str, log: bool = True):
    """
    Context manager for measuring execution time.

    Args:
        name: Name for the operation
        log: Whether to log the timing

    Example:
    --------
    ```python
    with measure_time("load_data"):
        data = db.query()
    ```
    """
    monitor = PerformanceMonitor()

    if monitor.is_enabled:
        timer_id = monitor.start_timer(name)
        try:
            yield
        finally:
            duration = monitor.stop_timer(timer_id)
            if log:
                logger.debug(f"[PERF] {name}: {duration:.2f}ms")
    else:
        yield


@contextmanager
def measure_memory(label: str, log: bool = True):
    """
    Context manager for measuring memory usage.

    Args:
        label: Label for the operation
        log: Whether to log memory changes

    Example:
    --------
    ```python
    with measure_memory("process_data"):
        process_large_dataset()
    ```
    """
    before = MemoryMonitor.get_usage()
    try:
        yield
    finally:
        after = MemoryMonitor.get_usage()
        growth = after.rss_bytes - before.rss_bytes

        if log:
            growth_mb = growth / (1024 * 1024)
            logger.debug(f"[MEM] {label}: {growth_mb:+.2f}MB")


# =============================================================================
# DECORATORS
# =============================================================================


def measure_performance(func: Optional[Callable] = None, name: Optional[str] = None):
    """
    Decorator to measure function performance.

    Can be used with or without parentheses.

    Example:
    --------
    ```python
    @measure_performance
    def slow_function():
        pass

    @measure_performance(name="custom_name")
    def another_function():
        pass
    ```
    """
    def decorator(fn: Callable) -> Callable:
        op_name = name or fn.__name__

        @wraps(fn)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()

            if monitor.is_enabled:
                timer_id = monitor.start_timer(op_name)
                try:
                    return fn(*args, **kwargs)
                finally:
                    monitor.stop_timer(timer_id)
            else:
                return fn(*args, **kwargs)

        return wrapper

    if func is not None:
        # Called without parentheses
        return decorator(func)
    return decorator


def log_slow(threshold_ms: float = 100, name: Optional[str] = None):
    """
    Decorator that logs a warning if function is slow.

    Args:
        threshold_ms: Time threshold in milliseconds
        name: Custom name for logging

    Example:
    --------
    ```python
    @log_slow(threshold_ms=500)
    def potentially_slow():
        pass
    ```
    """
    def decorator(func: Callable) -> Callable:
        op_name = name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                if duration_ms > threshold_ms:
                    logger.warning(
                        f"[SLOW] {op_name} took {duration_ms:.2f}ms "
                        f"(threshold: {threshold_ms}ms)"
                    )

        return wrapper
    return decorator


# =============================================================================
# PERFORMANCE WIDGET (for debugging UI)
# =============================================================================

# Note: This would normally import PySide6, but we'll define a stub
# The actual widget would be in app/ui/components/


class PerformanceWidget:
    """
    Debug widget for displaying performance stats.

    This is a stub - the actual widget would be in app/ui/components/
    and would use PySide6.

    Features:
    - Real-time stats display
    - Top 10 slowest operations
    - Memory usage graph
    - Toggle with Ctrl+Shift+P

    Would include:
    - QWidget subclass
    - QTimer for updates
    - QTableWidget for stats
    - Labels for memory info
    """

    def __init__(self):
        self._monitor = PerformanceMonitor()

    def get_display_data(self) -> Dict[str, Any]:
        """Get data for display."""
        return {
            "enabled": self._monitor.is_enabled,
            "summary": self._monitor.get_summary(),
            "memory": MemoryMonitor.get_usage().to_dict(),
            "top_operations": [
                s.to_dict() for s in self._monitor.get_top_operations(10)
            ],
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_monitor() -> PerformanceMonitor:
    """Get the singleton PerformanceMonitor instance."""
    return PerformanceMonitor()


def enable_monitoring() -> None:
    """Enable performance monitoring."""
    PerformanceMonitor().enable()


def disable_monitoring() -> None:
    """Disable performance monitoring."""
    PerformanceMonitor().disable()


def print_stats() -> None:
    """Print performance statistics to console."""
    monitor = PerformanceMonitor()
    summary = monitor.get_summary()

    print("\n=== Performance Statistics ===")
    print(f"Operations tracked: {summary['operations_tracked']}")
    print(f"Total calls: {summary['total_calls']}")
    print(f"Total time: {summary['total_time_ms']:.2f}ms")
    print("\nTop 5 by average time:")

    for stat in summary['top_5_avg']:
        print(f"  {stat['operation']}: avg={stat['avg_ms']:.2f}ms, "
              f"calls={stat['calls']}, max={stat['max_ms']:.2f}ms")

    mem = MemoryMonitor.get_usage()
    print(f"\nMemory: {mem.rss_mb:.1f}MB RSS, {mem.percent:.1f}%")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Data classes
    'PerformanceStats',
    'MemoryStats',

    # Main classes
    'PerformanceMonitor',
    'MemoryMonitor',

    # Context managers
    'measure_time',
    'measure_memory',

    # Decorators
    'measure_performance',
    'log_slow',

    # Helper functions
    'get_monitor',
    'enable_monitoring',
    'disable_monitoring',
    'print_stats',

    # Widget stub
    'PerformanceWidget',
]
