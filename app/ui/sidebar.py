"""
Sidebar Navigation - Menu navigasi untuk workflow pencairan dana
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
                               QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QColor


class SidebarNavigation(QWidget):
    """Sidebar dengan menu navigasi untuk sistem pencairan dana"""
    
    # Signals
    menu_clicked = Signal(str)  # Emit 'dashboard', 'up', 'tup', 'ls', etc.
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI sidebar"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QLabel('PENCAIRAN DANA')
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(12)
        header.setFont(header_font)
        header.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
            padding: 15px;
            border-bottom: 2px solid #34495e;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Menu items
        menu_items = [
            ('dashboard', '📊 Dashboard', '#95a5a6'),
            ('up', '💚 UP (Uang Persediaan)', '#27ae60'),
            ('tup', '🧡 TUP (Tambahan UP)', '#f39c12'),
            ('ls', '💙 LS (Pembayaran Langsung)', '#3498db'),
            ('separator', '', ''),
            ('pengadaan', '📦 Pengadaan', '#9b59b6'),
            ('pengguna', '👥 Pengguna', '#34495e'),
            ('pengaturan', '⚙️ Pengaturan', '#7f8c8d'),
        ]
        
        self.buttons = {}
        
        for menu_id, label, color in menu_items:
            if menu_id == 'separator':
                # Add separator
                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.HLine)
                sep.setFrameShadow(QFrame.Shadow.Sunken)
                sep.setStyleSheet("color: #bdc3c7;")
                layout.addWidget(sep)
                continue
            
            # Create button
            btn = QPushButton(label)
            btn.setMinimumHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, mid=menu_id: self.on_menu_clicked(mid))
            
            # Set stylesheet
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #34495e;
                    color: white;
                    border: none;
                    padding: 12px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 500;
                    border-left: 4px solid {color};
                }}
                QPushButton:hover {{
                    background-color: #2c3e50;
                }}
                QPushButton:pressed {{
                    background-color: #1a252f;
                }}
            """)
            
            layout.addWidget(btn)
            self.buttons[menu_id] = (btn, color)
        
        # Add stretch
        layout.addStretch()
        
        # Footer with version
        footer = QLabel('v1.0.0')
        footer.setStyleSheet("""
            color: #7f8c8d;
            padding: 10px;
            font-size: 11px;
            text-align: center;
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
        
        # Set fixed width
        self.setFixedWidth(250)
        self.setStyleSheet("background-color: #34495e;")
        self.setLayout(layout)
    
    def on_menu_clicked(self, menu_id: str):
        """Handle menu click"""
        self.set_active_menu(menu_id)
        self.menu_clicked.emit(menu_id)
    
    def set_active_menu(self, menu_id: str):
        """Set active menu item"""
        # Remove active style dari semua button
        for bid, (btn, color) in self.buttons.items():
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #34495e;
                    color: white;
                    border: none;
                    padding: 12px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 500;
                    border-left: 4px solid {color};
                }}
                QPushButton:hover {{
                    background-color: #2c3e50;
                }}
                QPushButton:pressed {{
                    background-color: #1a252f;
                }}
            """)
        
        # Add active style ke selected button
        if menu_id in self.buttons:
            btn, color = self.buttons[menu_id]
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 12px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 600;
                    border-left: 4px solid {color};
                }}
                QPushButton:hover {{
                    background-color: darker({color}, 120);
                }}
                QPushButton:pressed {{
                    background-color: darker({color}, 140);
                }}
            """)
        
        self.current_page = menu_id
