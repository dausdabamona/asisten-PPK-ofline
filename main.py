#!/usr/bin/env python3
"""
PPK DOCUMENT FACTORY v3.0
=========================
Template-Driven Procurement Workflow System

Main entry point untuk aplikasi.

Jalankan dengan:
    python main.py
    
Atau double-click START.bat di Windows
"""

import sys
import os

# Ensure app directory is in path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)


def check_dependencies():
    """Check if required packages are installed"""
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
        print("=" * 60)
        print("ERROR: Missing dependencies!")
        print("=" * 60)
        print("\nPlease install the following packages:")
        print(f"  pip install {' '.join(missing)}")
        print("\nOr run: pip install -r requirements.txt")
        print("=" * 60)
        sys.exit(1)


def create_sample_templates():
    """Create sample templates if not exist"""
    from app.core.config import WORD_TEMPLATES_DIR, EXCEL_TEMPLATES_DIR
    
    # Check if templates exist
    word_templates = os.listdir(WORD_TEMPLATES_DIR) if os.path.exists(WORD_TEMPLATES_DIR) else []
    excel_templates = os.listdir(EXCEL_TEMPLATES_DIR) if os.path.exists(EXCEL_TEMPLATES_DIR) else []
    
    if not word_templates and not excel_templates:
        print("Creating sample templates...")
        try:
            from create_templates import create_all_templates
            create_all_templates()
        except Exception as e:
            print(f"Warning: Could not create sample templates: {e}")


def main():
    """Main entry point"""
    print("=" * 60)
    print("PPK DOCUMENT FACTORY v3.0")
    print("Template-Driven Procurement Workflow System")
    print("=" * 60)
    
    # Check dependencies
    check_dependencies()
    
    # Create templates if needed
    create_sample_templates()
    
    print("\nStarting application...")
    
    # Import and run dashboard
    from app.ui.dashboard import main as run_dashboard
    run_dashboard()


if __name__ == "__main__":
    main()
