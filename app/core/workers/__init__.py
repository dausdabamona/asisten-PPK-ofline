"""
PPK Document Factory - Workers Package
======================================
Background workers for various operations.

This package provides specialized workers for:
- Document generation (single and batch)
- Database operations (load, save, export)
- Bulk operations

Base Classes (from parent module):
- WorkerSignals: Qt signals for communication
- BaseWorker: Abstract base class
- FunctionWorker: Generic function executor

Example Usage:
-------------
```python
# Document generation
from app.core.workers import DocumentGeneratorWorker, DocumentTask

worker = DocumentGeneratorWorker(
    template_name="HPS",
    data={"paket": "Test"},
    output_path="/output/hps.docx"
)
worker.signals.result.connect(on_complete)
worker.start()

# Batch documents
from app.core.workers import BatchDocumentWorker, DocumentTask

tasks = [
    DocumentTask("HPS", data1, "/output/hps1.docx"),
    DocumentTask("SPK", data2, "/output/spk1.docx"),
]
worker = BatchDocumentWorker(tasks)
worker.start()

# Data loading
from app.core.workers import DataLoadWorker

worker = DataLoadWorker(db.list_transaksi, mekanisme="UP")
worker.signals.result.connect(display_data)
worker.start()

# Export
from app.core.workers import ExportWorker, ExportFormat

worker = ExportWorker(data, ExportFormat.CSV, "/export/data.csv")
worker.start()
```
"""

# Import base classes from workers_base module
from ..workers_base import (
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

# Import document workers
from .document_worker import (
    DocumentTask,
    DocumentResult,
    BatchDocumentResult,
    DocumentGeneratorWorker,
    BatchDocumentWorker,
    DocumentExportWorker,
    create_document_worker,
    create_batch_worker,
)

# Import database workers
from .database_worker import (
    ExportFormat,
    LoadResult,
    SaveResult,
    ExportResult,
    BulkResult,
    DataLoadWorker,
    DataSaveWorker,
    ExportWorker,
    BulkOperationWorker,
    create_load_worker,
    create_save_worker,
    create_export_worker,
)


__all__ = [
    # =========================================================================
    # Base Classes (from parent)
    # =========================================================================
    'WorkerSignals',
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

    # =========================================================================
    # Document Workers
    # =========================================================================
    'DocumentTask',
    'DocumentResult',
    'BatchDocumentResult',
    'DocumentGeneratorWorker',
    'BatchDocumentWorker',
    'DocumentExportWorker',
    'create_document_worker',
    'create_batch_worker',

    # =========================================================================
    # Database Workers
    # =========================================================================
    'ExportFormat',
    'LoadResult',
    'SaveResult',
    'ExportResult',
    'BulkResult',
    'DataLoadWorker',
    'DataSaveWorker',
    'ExportWorker',
    'BulkOperationWorker',
    'create_load_worker',
    'create_save_worker',
    'create_export_worker',
]
