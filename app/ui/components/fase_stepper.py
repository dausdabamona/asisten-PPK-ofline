"""
Fase Stepper Component - Menampilkan progress fase dari 1-5 secara horizontal
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QColor


class FaseStep(QFrame):
    """Single step dalam stepper"""
    
    clicked = Signal(int)  # Signal when step clicked
    
    STATES = {
        'pending': {'bg': '#bdc3c7', 'text': '#ffffff', 'label': 'Menunggu'},
        'active': {'bg': '#3498db', 'text': '#ffffff', 'label': 'Aktif'},
        'completed': {'bg': '#27ae60', 'text': '#ffffff', 'label': 'Selesai'},
    }
    
    def __init__(self, fase_num: int, fase_name: str, state: str = 'pending'):
        super().__init__()
        self.fase_num = fase_num
        self.fase_name = fase_name
        self.state = state
        self.setStyleSheet("border: none;")
        self.setup_ui()
        self.set_state(state)
    
    def setup_ui(self):
        """Setup UI untuk step"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)
        
        # Nomor step
        self.step_label = QLabel(str(self.fase_num))
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.step_label.setFont(font)
        self.step_label.setFixedSize(QSize(40, 40))
        self.step_label.setStyleSheet(
            "border-radius: 20px; border: 2px solid transparent;"
        )
        
        # Nama step
        self.name_label = QLabel(self.fase_name)
        name_font = QFont()
        name_font.setPointSize(9)
        self.name_label.setFont(name_font)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setMaximumWidth(100)
        
        # State label
        self.state_label = QLabel(self.STATES['pending']['label'])
        state_font = QFont()
        state_font.setPointSize(7)
        self.state_label.setFont(state_font)
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.step_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.state_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def set_state(self, state: str):
        """Set state of step"""
        if state not in self.STATES:
            state = 'pending'
        
        self.state = state
        colors = self.STATES[state]
        
        self.step_label.setStyleSheet(f"""
            border-radius: 20px;
            background-color: {colors['bg']};
            color: {colors['text']};
            font-weight: bold;
            border: 2px solid {colors['bg']};
        """)
        
        self.state_label.setText(colors['label'])
    
    def mousePressEvent(self, event):
        """Handle click"""
        self.clicked.emit(self.fase_num)
        super().mousePressEvent(event)


class FaseConnector(QFrame):
    """Connector line antara steps"""
    
    def __init__(self, completed: bool = False):
        super().__init__()
        self.completed = completed
        self.setFixedHeight(6)
        self.setFixedWidth(50)
        self.setStyleSheet("border: none;")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI untuk connector"""
        color = '#27ae60' if self.completed else '#bdc3c7'
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: 3px;
        """)
    
    def set_completed(self, completed: bool):
        """Set connector sebagai completed"""
        self.completed = completed
        self.setup_ui()


class FaseStepper(QWidget):
    """Horizontal Fase Stepper - menampilkan progress 5 fase"""
    
    fase_changed = Signal(int)  # Signal when user click step
    
    def __init__(self, current_fase: int = 1, parent=None):
        super().__init__(parent)
        self.current_fase = current_fase
        self.steps = {}
        self.connectors = {}
        
        self.fase_names = {
            1: "Inisiasi",
            2: "Pencairan UM",
            3: "Pelaksanaan",
            4: "Pertanggung jawaban",
            5: "Penyelesaian"
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI untuk stepper"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(0)
        
        # Create steps and connectors
        for fase in range(1, 6):
            # Step
            state = 'completed' if fase < self.current_fase else \
                    'active' if fase == self.current_fase else 'pending'
            
            step = FaseStep(fase, self.fase_names[fase], state)
            step.clicked.connect(self.on_step_clicked)
            self.steps[fase] = step
            layout.addWidget(step)
            
            # Connector (tidak ada setelah step 5)
            if fase < 5:
                connector = FaseConnector(completed=fase < self.current_fase)
                self.connectors[fase] = connector
                layout.addWidget(connector)
        
        layout.addStretch()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #ffffff; border-radius: 8px;")
    
    def set_current_fase(self, fase: int):
        """Set current fase dan update stepper"""
        if 1 <= fase <= 5:
            self.current_fase = fase
            self.update_states()
    
    def update_states(self):
        """Update state semua steps berdasarkan current_fase"""
        for fase in range(1, 6):
            if fase < self.current_fase:
                self.steps[fase].set_state('completed')
            elif fase == self.current_fase:
                self.steps[fase].set_state('active')
            else:
                self.steps[fase].set_state('pending')
        
        # Update connectors
        for fase in range(1, 5):
            if fase < self.current_fase:
                self.connectors[fase].set_completed(True)
            else:
                self.connectors[fase].set_completed(False)
    
    def on_step_clicked(self, fase: int):
        """Handle step clicked"""
        # Hanya bisa click step yang sudah completed atau current
        if fase <= self.current_fase:
            self.set_current_fase(fase)
            self.fase_changed.emit(fase)
    
    def get_progress_percentage(self) -> int:
        """Get progress percentage (20% per fase)"""
        return (self.current_fase - 1) * 20


class FaseIndicator(QLabel):
    """Simple text indicator untuk fase"""
    
    def __init__(self, current_fase: int = 1, parent=None):
        super().__init__(parent)
        self.current_fase = current_fase
        self.update_text()
        
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
    
    def set_fase(self, fase: int):
        """Set current fase"""
        self.current_fase = fase
        self.update_text()
    
    def update_text(self):
        """Update text"""
        self.setText(f"Fase {self.current_fase}/5: {self._get_fase_name()}")
    
    def _get_fase_name(self) -> str:
        """Get nama fase"""
        names = {
            1: "Inisiasi & SK",
            2: "Pencairan Uang Muka",
            3: "Pelaksanaan Kegiatan",
            4: "Pertanggungjawaban",
            5: "Penyelesaian"
        }
        return names.get(self.current_fase, "Unknown")
