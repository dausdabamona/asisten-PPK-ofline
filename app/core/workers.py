"""
PPK Document Factory - Background Workers
==========================================
Worker classes for running operations in background threads.

This module provides:
- WorkerSignals: Qt signals for worker communication
- BaseWorker: Abstract base class for all workers
- FunctionWorker: Generic worker for running any function
- run_in_background: Convenience function for quick background tasks
- @background_task: Decorator for making functions run in background

Example Usage:
-------------
```python
# Option 1: FunctionWorker
worker = FunctionWorker(self.db.get_large_data, filter="active")
worker.signals.result.connect(self._on_data_loaded)
worker.signals.error.connect(self._on_error)
worker.start()

# Option 2: Helper function
run_in_background(
    self.db.get_large_data,
    on_result=self._on_data_loaded,
    on_error=self._on_error
)

# Option 3: Decorator
@background_task
def slow_function():
    # Will automatically run in separate thread
    pass
```
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Dict, List, Tuple
from functools import wraps
import traceback
import logging

from PySide6.QtCore import QObject, Signal, QThread, QMutex, QMutexLocker

logger = logging.getLogger(__name__)


# =============================================================================
# WORKER SIGNALS
# =============================================================================


class WorkerSignals(QObject):
    """
    Signals for worker communication.

    Signals:
        started: Emitted when worker starts
        finished: Emitted when worker completes (success or error)
        error: Emitted on error with error message
        result: Emitted on success with result object
        progress: Emitted during execution with progress (0-100)
        status: Emitted with status message
        cancelled: Emitted when worker is cancelled
    """

    started = Signal()
    finished = Signal()
    error = Signal(str)
    result = Signal(object)
    progress = Signal(int)  # 0-100
    status = Signal(str)
    cancelled = Signal()


# =============================================================================
# BASE WORKER
# =============================================================================


class BaseWorker(QThread):
    """
    Abstract base class for all background workers.

    Subclasses must implement the `do_work()` method.

    Features:
    - Automatic started/finished signal emission
    - Cancellation support
    - Progress reporting
    - Error handling

    Example:
    --------
    ```python
    class MyWorker(BaseWorker):
        def do_work(self):
            for i in range(100):
                if self.is_cancelled:
                    return None
                # Do work
                self.emit_progress(i + 1)
            return result
    ```
    """

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._signals = WorkerSignals()
        self._is_cancelled = False
        self._mutex = QMutex()
        self._result = None
        self._error: Optional[str] = None

    @property
    def signals(self) -> WorkerSignals:
        """Get worker signals object."""
        return self._signals

    @property
    def is_cancelled(self) -> bool:
        """Check if worker has been cancelled."""
        with QMutexLocker(self._mutex):
            return self._is_cancelled

    @property
    def result(self) -> Any:
        """Get the result after worker finishes."""
        return self._result

    @property
    def error(self) -> Optional[str]:
        """Get error message if worker failed."""
        return self._error

    def cancel(self) -> None:
        """
        Request cancellation of the worker.

        Note: The worker must check `is_cancelled` periodically
        and stop execution when it becomes True.
        """
        with QMutexLocker(self._mutex):
            self._is_cancelled = True
        logger.debug(f"Worker {self.__class__.__name__} cancellation requested")

    def emit_progress(self, value: int) -> None:
        """
        Emit progress signal.

        Args:
            value: Progress value (0-100)
        """
        # Clamp value to 0-100
        value = max(0, min(100, value))
        self._signals.progress.emit(value)

    def emit_status(self, message: str) -> None:
        """
        Emit status message.

        Args:
            message: Status message to emit
        """
        self._signals.status.emit(message)

    def run(self) -> None:
        """
        Main worker execution. Do not override this method.
        Override `do_work()` instead.
        """
        self._signals.started.emit()
        logger.debug(f"Worker {self.__class__.__name__} started")

        try:
            # Check for early cancellation
            if self.is_cancelled:
                self._signals.cancelled.emit()
                self._signals.finished.emit()
                return

            # Execute the actual work
            self._result = self.do_work()

            # Check if cancelled during work
            if self.is_cancelled:
                self._signals.cancelled.emit()
            else:
                self._signals.result.emit(self._result)

        except Exception as e:
            self._error = str(e)
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Worker {self.__class__.__name__} error: {error_msg}")
            logger.debug(traceback.format_exc())
            self._signals.error.emit(error_msg)

        finally:
            self._signals.finished.emit()
            logger.debug(f"Worker {self.__class__.__name__} finished")

    @abstractmethod
    def do_work(self) -> Any:
        """
        Implement the actual work in this method.

        Override this method in subclasses to perform the background task.

        Returns:
            The result of the work, which will be emitted via signals.result

        Raises:
            Any exception will be caught and emitted via signals.error
        """
        raise NotImplementedError("Subclasses must implement do_work()")


# =============================================================================
# FUNCTION WORKER
# =============================================================================


class FunctionWorker(BaseWorker):
    """
    Generic worker for running any callable in background.

    Example:
    --------
    ```python
    # Run a function with arguments
    worker = FunctionWorker(db.get_data, filter="active", limit=100)
    worker.signals.result.connect(handle_result)
    worker.signals.error.connect(handle_error)
    worker.start()

    # Run a lambda
    worker = FunctionWorker(lambda: expensive_calculation())
    worker.start()
    ```
    """

    def __init__(
        self,
        func: Callable,
        *args,
        parent: Optional[QObject] = None,
        **kwargs
    ):
        """
        Initialize FunctionWorker.

        Args:
            func: The function to execute
            *args: Positional arguments to pass to func
            parent: Parent QObject
            **kwargs: Keyword arguments to pass to func
        """
        super().__init__(parent)
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def do_work(self) -> Any:
        """Execute the stored function with arguments."""
        return self._func(*self._args, **self._kwargs)


# =============================================================================
# PROGRESS FUNCTION WORKER
# =============================================================================


class ProgressFunctionWorker(BaseWorker):
    """
    Worker for functions that report progress.

    The function receives a `progress_callback` that it can call
    to report progress.

    Example:
    --------
    ```python
    def process_items(items, progress_callback):
        total = len(items)
        for i, item in enumerate(items):
            process(item)
            progress_callback((i + 1) * 100 // total)
        return "done"

    worker = ProgressFunctionWorker(process_items, items)
    worker.signals.progress.connect(update_progress_bar)
    worker.start()
    ```
    """

    def __init__(
        self,
        func: Callable,
        *args,
        parent: Optional[QObject] = None,
        **kwargs
    ):
        """
        Initialize ProgressFunctionWorker.

        Args:
            func: Function that accepts progress_callback as first argument
            *args: Additional positional arguments
            parent: Parent QObject
            **kwargs: Keyword arguments
        """
        super().__init__(parent)
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def do_work(self) -> Any:
        """Execute function with progress callback."""
        return self._func(self.emit_progress, *self._args, **self._kwargs)


# =============================================================================
# BATCH WORKER
# =============================================================================


class BatchWorker(BaseWorker):
    """
    Worker for processing items in batches.

    Example:
    --------
    ```python
    def process_item(item):
        return item * 2

    worker = BatchWorker(process_item, items=[1, 2, 3, 4, 5])
    worker.signals.result.connect(handle_results)  # [2, 4, 6, 8, 10]
    worker.start()
    ```
    """

    def __init__(
        self,
        process_func: Callable[[Any], Any],
        items: List[Any],
        parent: Optional[QObject] = None,
        continue_on_error: bool = True
    ):
        """
        Initialize BatchWorker.

        Args:
            process_func: Function to process each item
            items: List of items to process
            parent: Parent QObject
            continue_on_error: If True, continue processing on errors
        """
        super().__init__(parent)
        self._process_func = process_func
        self._items = items
        self._continue_on_error = continue_on_error
        self._errors: List[Tuple[int, str]] = []

    @property
    def errors(self) -> List[Tuple[int, str]]:
        """Get list of (index, error_message) for failed items."""
        return self._errors

    def do_work(self) -> List[Any]:
        """Process all items and return results."""
        results = []
        total = len(self._items)

        for i, item in enumerate(self._items):
            if self.is_cancelled:
                break

            try:
                result = self._process_func(item)
                results.append(result)
            except Exception as e:
                error_msg = f"Item {i}: {str(e)}"
                self._errors.append((i, str(e)))
                logger.warning(f"BatchWorker error: {error_msg}")

                if not self._continue_on_error:
                    raise

                results.append(None)

            # Update progress
            progress = (i + 1) * 100 // total
            self.emit_progress(progress)
            self.emit_status(f"Memproses {i + 1}/{total}")

        return results


# =============================================================================
# SEQUENTIAL WORKER
# =============================================================================


class SequentialWorker(BaseWorker):
    """
    Worker for running multiple tasks sequentially.

    Example:
    --------
    ```python
    worker = SequentialWorker([
        ("Load data", load_data),
        ("Process", process_data),
        ("Save", save_result),
    ])
    worker.signals.status.connect(update_status)
    worker.start()
    ```
    """

    def __init__(
        self,
        tasks: List[Tuple[str, Callable]],
        parent: Optional[QObject] = None,
        pass_result: bool = True
    ):
        """
        Initialize SequentialWorker.

        Args:
            tasks: List of (name, function) tuples
            parent: Parent QObject
            pass_result: If True, pass result of each task to the next
        """
        super().__init__(parent)
        self._tasks = tasks
        self._pass_result = pass_result

    def do_work(self) -> Any:
        """Execute tasks sequentially."""
        total = len(self._tasks)
        result = None

        for i, (name, func) in enumerate(self._tasks):
            if self.is_cancelled:
                break

            self.emit_status(name)
            logger.debug(f"SequentialWorker executing: {name}")

            try:
                if self._pass_result and result is not None:
                    result = func(result)
                else:
                    result = func()
            except Exception as e:
                logger.error(f"SequentialWorker failed at '{name}': {e}")
                raise

            progress = (i + 1) * 100 // total
            self.emit_progress(progress)

        return result


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def run_in_background(
    func: Callable,
    *args,
    on_result: Optional[Callable[[Any], None]] = None,
    on_error: Optional[Callable[[str], None]] = None,
    on_progress: Optional[Callable[[int], None]] = None,
    on_finished: Optional[Callable[[], None]] = None,
    on_started: Optional[Callable[[], None]] = None,
    parent: Optional[QObject] = None,
    **kwargs
) -> FunctionWorker:
    """
    Convenience function to run a function in background.

    Args:
        func: Function to execute
        *args: Positional arguments for func
        on_result: Callback for successful result
        on_error: Callback for errors
        on_progress: Callback for progress updates
        on_finished: Callback when worker finishes
        on_started: Callback when worker starts
        parent: Parent QObject for worker
        **kwargs: Keyword arguments for func

    Returns:
        FunctionWorker instance (can be used to cancel)

    Example:
    --------
    ```python
    worker = run_in_background(
        db.load_data,
        filter="active",
        on_result=self.display_data,
        on_error=self.show_error
    )

    # Cancel if needed
    worker.cancel()
    ```
    """
    worker = FunctionWorker(func, *args, parent=parent, **kwargs)

    if on_result:
        worker.signals.result.connect(on_result)
    if on_error:
        worker.signals.error.connect(on_error)
    if on_progress:
        worker.signals.progress.connect(on_progress)
    if on_finished:
        worker.signals.finished.connect(on_finished)
    if on_started:
        worker.signals.started.connect(on_started)

    worker.start()
    return worker


def run_with_progress(
    func: Callable,
    *args,
    on_result: Optional[Callable[[Any], None]] = None,
    on_error: Optional[Callable[[str], None]] = None,
    on_progress: Optional[Callable[[int], None]] = None,
    parent: Optional[QObject] = None,
    **kwargs
) -> ProgressFunctionWorker:
    """
    Run a function that reports progress in background.

    The function should accept a progress_callback as its first argument.

    Args:
        func: Function that accepts (progress_callback, *args, **kwargs)
        *args: Additional arguments
        on_result: Result callback
        on_error: Error callback
        on_progress: Progress callback
        parent: Parent QObject
        **kwargs: Keyword arguments

    Returns:
        ProgressFunctionWorker instance
    """
    worker = ProgressFunctionWorker(func, *args, parent=parent, **kwargs)

    if on_result:
        worker.signals.result.connect(on_result)
    if on_error:
        worker.signals.error.connect(on_error)
    if on_progress:
        worker.signals.progress.connect(on_progress)

    worker.start()
    return worker


# =============================================================================
# DECORATORS
# =============================================================================


def background_task(
    on_result: Optional[Callable[[Any], None]] = None,
    on_error: Optional[Callable[[str], None]] = None,
    on_progress: Optional[Callable[[int], None]] = None
):
    """
    Decorator to make a function run in background thread.

    The decorated function will return a FunctionWorker instead of
    executing directly.

    Example:
    --------
    ```python
    @background_task(on_result=handle_result)
    def slow_calculation(x, y):
        time.sleep(5)
        return x + y

    # Returns worker immediately, executes in background
    worker = slow_calculation(10, 20)
    ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return run_in_background(
                func, *args,
                on_result=on_result,
                on_error=on_error,
                on_progress=on_progress,
                **kwargs
            )
        return wrapper
    return decorator


def async_slot(*types):
    """
    Decorator for Qt slots that should run in background.

    Useful for slots connected to UI signals that perform
    heavy operations.

    Example:
    --------
    ```python
    @async_slot()
    def on_button_clicked(self):
        # This runs in background thread
        return self.load_heavy_data()
    ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return run_in_background(
                func, self, *args,
                parent=self if isinstance(self, QObject) else None,
                **kwargs
            )
        return wrapper
    return decorator


# =============================================================================
# WORKER POOL
# =============================================================================


class WorkerPool:
    """
    Pool for managing multiple workers.

    Provides tracking and bulk operations for workers.

    Example:
    --------
    ```python
    pool = WorkerPool()

    worker1 = pool.submit(FunctionWorker(func1))
    worker2 = pool.submit(FunctionWorker(func2))

    # Cancel all workers
    pool.cancel_all()

    # Wait for all to finish
    pool.wait_all()
    ```
    """

    def __init__(self):
        self._workers: List[BaseWorker] = []
        self._mutex = QMutex()

    def submit(self, worker: BaseWorker) -> BaseWorker:
        """
        Add and start a worker.

        Args:
            worker: Worker to add

        Returns:
            The same worker for chaining
        """
        with QMutexLocker(self._mutex):
            self._workers.append(worker)

        # Remove from list when finished
        worker.signals.finished.connect(lambda: self._remove_worker(worker))
        worker.start()

        return worker

    def _remove_worker(self, worker: BaseWorker) -> None:
        """Remove worker from pool."""
        with QMutexLocker(self._mutex):
            if worker in self._workers:
                self._workers.remove(worker)

    def cancel_all(self) -> None:
        """Cancel all workers in pool."""
        with QMutexLocker(self._mutex):
            for worker in self._workers:
                worker.cancel()

    def wait_all(self, timeout_ms: int = -1) -> bool:
        """
        Wait for all workers to finish.

        Args:
            timeout_ms: Timeout in milliseconds (-1 for infinite)

        Returns:
            True if all finished, False if timeout
        """
        with QMutexLocker(self._mutex):
            workers = list(self._workers)

        for worker in workers:
            if not worker.wait(timeout_ms):
                return False
        return True

    @property
    def active_count(self) -> int:
        """Get number of active workers."""
        with QMutexLocker(self._mutex):
            return len(self._workers)

    @property
    def is_busy(self) -> bool:
        """Check if any workers are running."""
        return self.active_count > 0


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Signals
    'WorkerSignals',

    # Workers
    'BaseWorker',
    'FunctionWorker',
    'ProgressFunctionWorker',
    'BatchWorker',
    'SequentialWorker',

    # Helper functions
    'run_in_background',
    'run_with_progress',

    # Decorators
    'background_task',
    'async_slot',

    # Pool
    'WorkerPool',
]
