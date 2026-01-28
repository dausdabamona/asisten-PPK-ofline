"""
PPK DOCUMENT FACTORY v4.0 - Workflow Edition
=============================================
Workflow-based pencairan dana management system.

Modules:
- core: Configuration and database
- models: Pencairan dana models
- config: Workflow configurations
- templates: Document generation engine
- workflow: Workflow state management
- ui: PySide6 user interface
"""

__version__ = "4.0.0"
__author__ = "PPK Digital Assistant"


def get_main_window():
    """Get the main window class (lazy import to avoid PySide6 import at module load)."""
    from .ui.main_window_v2 import MainWindowV2
    return MainWindowV2
