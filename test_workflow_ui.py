"""
Test Workflow UI - Script untuk test workflow main window
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from app.ui.workflow_main_window import WorkflowMainWindow


def main():
    app = QApplication(sys.argv)
    
    # Load QSS stylesheet
    qss_path = os.path.join(
        os.path.dirname(__file__),
        'app', 'ui', 'styles', 'main.qss'
    )
    if os.path.exists(qss_path):
        with open(qss_path, 'r') as f:
            stylesheet = f.read()
            app.setStyleSheet(stylesheet)
    
    # Create and show main window
    window = WorkflowMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
