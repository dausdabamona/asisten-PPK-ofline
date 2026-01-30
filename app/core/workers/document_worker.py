"""
PPK Document Factory - Document Workers
=======================================
Background workers for document generation operations.

Workers:
- DocumentGeneratorWorker: Generate single document
- BatchDocumentWorker: Generate multiple documents
- DocumentExportWorker: Export documents to different formats
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
import logging
import time

from PySide6.QtCore import QObject

from ..workers import BaseWorker

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class DocumentTask:
    """
    Configuration for a single document generation task.

    Attributes:
        template_name: Name of template to use (e.g., "HPS", "SPK", "SPMK")
        data: Dictionary of data to fill template with
        output_path: Path where generated document will be saved
        output_format: Output format ("docx", "pdf", "xlsx")
        metadata: Additional metadata for the document
    """
    template_name: str
    data: Dict[str, Any]
    output_path: str
    output_format: str = "docx"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Ensure output_path is a Path object internally
        self._output_path = Path(self.output_path)

    @property
    def filename(self) -> str:
        """Get output filename."""
        return self._output_path.name


@dataclass
class DocumentResult:
    """
    Result of document generation.

    Attributes:
        success: Whether generation was successful
        output_path: Path to generated document
        error_message: Error message if failed
        generation_time: Time taken in seconds
        file_size: Size of generated file in bytes
    """
    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    generation_time: float = 0.0
    file_size: int = 0


@dataclass
class BatchDocumentResult:
    """
    Result of batch document generation.

    Attributes:
        total: Total number of documents
        successful: Number of successfully generated documents
        failed: Number of failed documents
        results: List of individual DocumentResult objects
        total_time: Total time taken in seconds
    """
    total: int = 0
    successful: int = 0
    failed: int = 0
    results: List[DocumentResult] = field(default_factory=list)
    total_time: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total == 0:
            return 0.0
        return (self.successful / self.total) * 100


# =============================================================================
# DOCUMENT GENERATOR WORKER
# =============================================================================


class DocumentGeneratorWorker(BaseWorker):
    """
    Worker for generating a single document in background.

    Generates a document from template with provided data.

    Example:
    --------
    ```python
    worker = DocumentGeneratorWorker(
        template_name="HPS",
        data={"paket_nama": "Pengadaan ATK", "nilai": 50000000},
        output_path="/path/to/output/HPS_001.docx"
    )
    worker.signals.result.connect(self._on_document_ready)
    worker.signals.progress.connect(self._update_progress)
    worker.signals.error.connect(self._on_error)
    worker.start()
    ```
    """

    def __init__(
        self,
        template_name: str,
        data: Dict[str, Any],
        output_path: str,
        generator: Optional[Any] = None,
        parent: Optional[QObject] = None
    ):
        """
        Initialize DocumentGeneratorWorker.

        Args:
            template_name: Name of template to use
            data: Data dictionary to fill template
            output_path: Path for output document
            generator: Optional DokumenGenerator instance (will create if None)
            parent: Parent QObject
        """
        super().__init__(parent)
        self._template_name = template_name
        self._data = data
        self._output_path = Path(output_path)
        self._generator = generator

    def do_work(self) -> DocumentResult:
        """Generate the document."""
        start_time = time.time()

        try:
            self.emit_progress(10)
            self.emit_status(f"Memuat template {self._template_name}...")

            # Get or create generator
            generator = self._generator
            if generator is None:
                from ...services.dokumen_generator import get_dokumen_generator
                generator = get_dokumen_generator()

            if self.is_cancelled:
                return DocumentResult(success=False, error_message="Dibatalkan")

            self.emit_progress(30)
            self.emit_status("Mengisi data ke template...")

            # Ensure output directory exists
            self._output_path.parent.mkdir(parents=True, exist_ok=True)

            if self.is_cancelled:
                return DocumentResult(success=False, error_message="Dibatalkan")

            self.emit_progress(50)

            # Generate document
            output_file = generator.generate(
                template_name=self._template_name,
                data=self._data,
                output_path=str(self._output_path)
            )

            if self.is_cancelled:
                return DocumentResult(success=False, error_message="Dibatalkan")

            self.emit_progress(90)
            self.emit_status("Menyimpan dokumen...")

            # Get file size
            file_size = 0
            if Path(output_file).exists():
                file_size = Path(output_file).stat().st_size

            self.emit_progress(100)

            generation_time = time.time() - start_time
            logger.info(
                f"Generated document {self._template_name} "
                f"in {generation_time:.2f}s ({file_size} bytes)"
            )

            return DocumentResult(
                success=True,
                output_path=str(output_file),
                generation_time=generation_time,
                file_size=file_size
            )

        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Document generation failed: {error_msg}")

            return DocumentResult(
                success=False,
                error_message=error_msg,
                generation_time=generation_time
            )


# =============================================================================
# BATCH DOCUMENT WORKER
# =============================================================================


class BatchDocumentWorker(BaseWorker):
    """
    Worker for generating multiple documents in batch.

    Processes a list of DocumentTask objects and generates
    all documents, reporting progress along the way.

    Example:
    --------
    ```python
    tasks = [
        DocumentTask("HPS", data1, "/output/HPS_001.docx"),
        DocumentTask("SPK", data2, "/output/SPK_001.docx"),
        DocumentTask("SPMK", data3, "/output/SPMK_001.docx"),
    ]

    worker = BatchDocumentWorker(tasks)
    worker.signals.progress.connect(self._update_progress)
    worker.signals.result.connect(self._on_batch_complete)
    worker.start()
    ```
    """

    def __init__(
        self,
        documents: List[DocumentTask],
        generator: Optional[Any] = None,
        parent: Optional[QObject] = None,
        continue_on_error: bool = True
    ):
        """
        Initialize BatchDocumentWorker.

        Args:
            documents: List of DocumentTask to process
            generator: Optional DokumenGenerator instance
            parent: Parent QObject
            continue_on_error: Continue processing if one document fails
        """
        super().__init__(parent)
        self._documents = documents
        self._generator = generator
        self._continue_on_error = continue_on_error

    def do_work(self) -> BatchDocumentResult:
        """Generate all documents."""
        start_time = time.time()
        total = len(self._documents)
        results = []
        successful = 0
        failed = 0

        # Get or create generator
        generator = self._generator
        if generator is None:
            try:
                from ...services.dokumen_generator import get_dokumen_generator
                generator = get_dokumen_generator()
            except Exception as e:
                logger.error(f"Failed to get document generator: {e}")
                return BatchDocumentResult(
                    total=total,
                    successful=0,
                    failed=total,
                    results=[
                        DocumentResult(
                            success=False,
                            error_message=f"Generator error: {e}"
                        )
                        for _ in self._documents
                    ],
                    total_time=time.time() - start_time
                )

        for i, task in enumerate(self._documents):
            if self.is_cancelled:
                # Mark remaining as cancelled
                for _ in range(i, total):
                    results.append(DocumentResult(
                        success=False,
                        error_message="Dibatalkan"
                    ))
                    failed += 1
                break

            # Update progress
            progress = (i * 100) // total
            self.emit_progress(progress)
            self.emit_status(f"Menghasilkan {task.template_name} ({i + 1}/{total})...")

            task_start = time.time()

            try:
                # Ensure output directory exists
                output_path = Path(task.output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Generate document
                output_file = generator.generate(
                    template_name=task.template_name,
                    data=task.data,
                    output_path=str(output_path)
                )

                # Get file size
                file_size = 0
                if Path(output_file).exists():
                    file_size = Path(output_file).stat().st_size

                results.append(DocumentResult(
                    success=True,
                    output_path=str(output_file),
                    generation_time=time.time() - task_start,
                    file_size=file_size
                ))
                successful += 1

            except Exception as e:
                error_msg = str(e)
                logger.error(
                    f"Failed to generate {task.template_name}: {error_msg}"
                )

                results.append(DocumentResult(
                    success=False,
                    error_message=error_msg,
                    generation_time=time.time() - task_start
                ))
                failed += 1

                if not self._continue_on_error:
                    # Mark remaining as skipped
                    for _ in range(i + 1, total):
                        results.append(DocumentResult(
                            success=False,
                            error_message="Dilewati karena error sebelumnya"
                        ))
                        failed += 1
                    break

        self.emit_progress(100)
        total_time = time.time() - start_time

        logger.info(
            f"Batch generation complete: {successful}/{total} successful "
            f"in {total_time:.2f}s"
        )

        return BatchDocumentResult(
            total=total,
            successful=successful,
            failed=failed,
            results=results,
            total_time=total_time
        )


# =============================================================================
# DOCUMENT EXPORT WORKER
# =============================================================================


class DocumentExportWorker(BaseWorker):
    """
    Worker for exporting documents to different formats.

    Supports conversion between formats (docx -> pdf, etc.)

    Example:
    --------
    ```python
    worker = DocumentExportWorker(
        input_path="/path/to/document.docx",
        output_path="/path/to/document.pdf",
        output_format="pdf"
    )
    worker.signals.result.connect(self._on_export_complete)
    worker.start()
    ```
    """

    def __init__(
        self,
        input_path: str,
        output_path: str,
        output_format: str = "pdf",
        parent: Optional[QObject] = None
    ):
        """
        Initialize DocumentExportWorker.

        Args:
            input_path: Path to input document
            output_path: Path for exported document
            output_format: Target format ("pdf", "docx", "xlsx")
            parent: Parent QObject
        """
        super().__init__(parent)
        self._input_path = Path(input_path)
        self._output_path = Path(output_path)
        self._output_format = output_format.lower()

    def do_work(self) -> DocumentResult:
        """Export the document."""
        start_time = time.time()

        try:
            self.emit_progress(10)
            self.emit_status("Membaca dokumen sumber...")

            if not self._input_path.exists():
                raise FileNotFoundError(
                    f"File tidak ditemukan: {self._input_path}"
                )

            self.emit_progress(30)
            self.emit_status(f"Mengkonversi ke {self._output_format.upper()}...")

            # Ensure output directory exists
            self._output_path.parent.mkdir(parents=True, exist_ok=True)

            if self.is_cancelled:
                return DocumentResult(success=False, error_message="Dibatalkan")

            # Perform conversion based on format
            if self._output_format == "pdf":
                self._convert_to_pdf()
            elif self._output_format == "docx":
                self._convert_to_docx()
            elif self._output_format == "xlsx":
                self._convert_to_xlsx()
            else:
                raise ValueError(f"Format tidak didukung: {self._output_format}")

            self.emit_progress(90)
            self.emit_status("Menyimpan hasil...")

            # Get file size
            file_size = 0
            if self._output_path.exists():
                file_size = self._output_path.stat().st_size

            self.emit_progress(100)
            generation_time = time.time() - start_time

            return DocumentResult(
                success=True,
                output_path=str(self._output_path),
                generation_time=generation_time,
                file_size=file_size
            )

        except Exception as e:
            return DocumentResult(
                success=False,
                error_message=str(e),
                generation_time=time.time() - start_time
            )

    def _convert_to_pdf(self) -> None:
        """Convert document to PDF format."""
        # Try using LibreOffice/OpenOffice if available
        import subprocess
        import shutil

        # Check for LibreOffice
        libreoffice_path = shutil.which("libreoffice") or shutil.which("soffice")

        if libreoffice_path:
            # Use LibreOffice for conversion
            output_dir = str(self._output_path.parent)
            subprocess.run([
                libreoffice_path,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", output_dir,
                str(self._input_path)
            ], check=True)

            # Rename to target path if different
            generated_pdf = self._input_path.with_suffix(".pdf")
            if generated_pdf != self._output_path:
                if generated_pdf.exists():
                    generated_pdf.rename(self._output_path)
        else:
            # Fallback: copy with message (or use python-docx2pdf if available)
            try:
                from docx2pdf import convert
                convert(str(self._input_path), str(self._output_path))
            except ImportError:
                raise RuntimeError(
                    "Konversi PDF memerlukan LibreOffice atau python-docx2pdf"
                )

    def _convert_to_docx(self) -> None:
        """Convert to DOCX format (copy if already docx)."""
        import shutil
        shutil.copy2(self._input_path, self._output_path)

    def _convert_to_xlsx(self) -> None:
        """Convert to XLSX format."""
        import shutil
        # For now, just copy if the source is already xlsx
        if self._input_path.suffix.lower() == ".xlsx":
            shutil.copy2(self._input_path, self._output_path)
        else:
            raise ValueError(
                f"Konversi dari {self._input_path.suffix} ke xlsx tidak didukung"
            )


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_document_worker(
    template_name: str,
    data: Dict[str, Any],
    output_path: str,
    **kwargs
) -> DocumentGeneratorWorker:
    """
    Create a document generator worker.

    Args:
        template_name: Template name
        data: Data dictionary
        output_path: Output file path
        **kwargs: Additional arguments for worker

    Returns:
        DocumentGeneratorWorker instance
    """
    return DocumentGeneratorWorker(
        template_name=template_name,
        data=data,
        output_path=output_path,
        **kwargs
    )


def create_batch_worker(
    documents: List[DocumentTask],
    **kwargs
) -> BatchDocumentWorker:
    """
    Create a batch document worker.

    Args:
        documents: List of document tasks
        **kwargs: Additional arguments for worker

    Returns:
        BatchDocumentWorker instance
    """
    return BatchDocumentWorker(documents=documents, **kwargs)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Data classes
    'DocumentTask',
    'DocumentResult',
    'BatchDocumentResult',

    # Workers
    'DocumentGeneratorWorker',
    'BatchDocumentWorker',
    'DocumentExportWorker',

    # Factory functions
    'create_document_worker',
    'create_batch_worker',
]
