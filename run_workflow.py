#!/usr/bin/env python3
"""
PPK DOCUMENT FACTORY - Workflow Edition Launcher
=================================================
Launch script for the new workflow-based UI.

Usage:
    python run_workflow.py
"""

import sys
import os

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

def check_dependencies():
    """Check if all required dependencies are installed."""
    missing = []

    try:
        import PySide6
    except ImportError:
        missing.append("PySide6")

    try:
        import docx
    except ImportError:
        missing.append("python-docx")

    try:
        import openpyxl
    except ImportError:
        missing.append("openpyxl")

    if missing:
        print("Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstall with: pip install " + " ".join(missing))
        return False

    return True


def main():
    """Main entry point."""
    print("PPK Document Factory v4.0 - Workflow Edition")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Launch application
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QFont

    from app.ui.main_window_v2 import MainWindowV2

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Create and show main window
    window = MainWindowV2()
    window.show()

    print("Application started. Close the window to exit.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
