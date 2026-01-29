"""
Dashboard Styles
================
Stylesheet definitions for dashboard components.

Author: PPK Document Factory Team
Version: 1.0
"""

# Main Dashboard Stylesheet
DASHBOARD_STYLE = """
QMainWindow {
    background-color: #f0f2f5;
}

QGroupBox {
    font-weight: bold;
    border: 1px solid #d0d0d0;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 10px;
    background-color: white;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px;
    color: #2c3e50;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #1f6dad;
}

QPushButton:disabled {
    background-color: #bdc3c7;
    color: #7f8c8d;
}

QPushButton#btnSuccess {
    background-color: #27ae60;
}
QPushButton#btnSuccess:hover {
    background-color: #219a52;
}

QPushButton#btnWarning {
    background-color: #e67e22;
}
QPushButton#btnWarning:hover {
    background-color: #d35400;
}

QPushButton#btnDanger {
    background-color: #e74c3c;
}
QPushButton#btnDanger:hover {
    background-color: #c0392b;
}

QPushButton#btnSecondary {
    background-color: #95a5a6;
}
QPushButton#btnSecondary:hover {
    background-color: #7f8c8d;
}

QLabel#titleLabel {
    font-size: 24px;
    font-weight: bold;
    color: #2c3e50;
}

QTableWidget {
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background-color: white;
}

QLineEdit, QComboBox, QDateEdit {
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 8px;
    background-color: white;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 2px solid #3498db;
}

QProgressBar {
    border: 1px solid #d0d0d0;
    border-radius: 5px;
    text-align: center;
    background-color: #ecf0f1;
}

QProgressBar::chunk {
    background-color: #27ae60;
    border-radius: 4px;
}

QListWidget {
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background-color: white;
}

QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #ecf0f1;
}

QListWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QTreeWidget {
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background-color: white;
}

QStatusBar {
    background-color: #34495e;
    color: white;
}
"""

# Color palette constants
COLORS = {
    'primary': '#3498db',
    'primary_hover': '#2980b9',
    'primary_pressed': '#1f6dad',
    'success': '#27ae60',
    'success_hover': '#219a52',
    'warning': '#e67e22',
    'warning_hover': '#d35400',
    'danger': '#e74c3c',
    'danger_hover': '#c0392b',
    'secondary': '#95a5a6',
    'secondary_hover': '#7f8c8d',
    'disabled_bg': '#bdc3c7',
    'disabled_text': '#7f8c8d',
    'background': '#f0f2f5',
    'surface': 'white',
    'border': '#d0d0d0',
    'text_primary': '#2c3e50',
    'text_secondary': '#7f8c8d',
}
