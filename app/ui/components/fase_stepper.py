"""
PPK DOCUMENT FACTORY - Fase Stepper Component
==============================================
Stepper horizontal untuk menampilkan progress fase workflow.

Features:
- 5 step dengan icon dan label
- State: completed, active, pending
- Clickable untuk navigasi antar fase
- Connector line antar step
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from typing import Dict, Any, List, Optional


class FaseStep(QWidget):
    """Individual step dalam stepper."""

    clicked = Signal(int)

    STATE_STYLES = {
        "completed": {
            "bg": "#27ae60",
            "border": "#1e8449",
            "text": "#ffffff",
            "label": "#27ae60"
        },
        "active": {
            "bg": "#3498db",
            "border": "#2980b9",
            "text": "#ffffff",
            "label": "#3498db"
        },
        "pending": {
            "bg": "#bdc3c7",
            "border": "#95a5a6",
            "text": "#ffffff",
            "label": "#7f8c8d"
        },
        "locked": {
            "bg": "#95a5a6",
            "border": "#7f8c8d",
            "text": "#7f8c8d",
            "label": "#95a5a6"
        }
    }

    def __init__(
        self,
        fase_num: int,
        nama: str,
        state: str = "pending",
        parent=None
    ):
        super().__init__(parent)
        self.fase_num = fase_num
        self.nama = nama
        self._state = state

        self._setup_ui()
        self._update_style()

    def _setup_ui(self):
        """Setup step UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        # Circle button
        self.circle = QPushButton(str(self.fase_num))
        self.circle.setFixedSize(44, 44)
        self.circle.setCursor(Qt.PointingHandCursor)
        self.circle.clicked.connect(lambda: self.clicked.emit(self.fase_num))
        layout.addWidget(self.circle, alignment=Qt.AlignCenter)

        # Label
        self.label = QLabel(self.nama)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setFixedWidth(80)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

    def _update_style(self):
        """Update styling based on state."""
        styles = self.STATE_STYLES.get(self._state, self.STATE_STYLES["pending"])

        # Circle style
        border_width = "3px" if self._state == "active" else "2px"
        self.circle.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles['bg']};
                color: {styles['text']};
                border: {border_width} solid {styles['border']};
                border-radius: 22px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {styles['border']};
            }}
        """)

        # Label style
        font_weight = "bold" if self._state in ["active", "completed"] else "normal"
        self.label.setStyleSheet(f"""
            font-size: 11px;
            color: {styles['label']};
            font-weight: {font_weight};
        """)

    def set_state(self, state: str):
        """Set step state."""
        if state in self.STATE_STYLES:
            self._state = state
            self._update_style()

    def get_state(self) -> str:
        """Get current state."""
        return self._state


class FaseConnector(QFrame):
    """Connector line between steps."""

    def __init__(self, completed: bool = False, parent=None):
        super().__init__(parent)
        self._completed = completed
        self.setFixedHeight(4)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._update_style()

    def _update_style(self):
        """Update connector style."""
        color = "#27ae60" if self._completed else "#bdc3c7"
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: 2px;
        """)

    def set_completed(self, completed: bool):
        """Set completion state."""
        self._completed = completed
        self._update_style()


class FaseStepper(QFrame):
    """
    Horizontal stepper untuk workflow fase.

    Signals:
        fase_clicked(int): Emitted when a fase step is clicked
    """

    fase_clicked = Signal(int)

    def __init__(
        self,
        mekanisme: str = "UP",
        fase_aktif: int = 1,
        parent=None
    ):
        super().__init__(parent)
        self.mekanisme = mekanisme.upper()
        self.fase_aktif = fase_aktif
        self._steps: Dict[int, FaseStep] = {}
        self._connectors: List[FaseConnector] = []

        self._setup_ui()
        self._add_shadow()

    def _setup_ui(self):
        """Setup stepper UI."""
        self.setObjectName("faseStepper")
        self.setStyleSheet("""
            #faseStepper {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(0)

        # Title
        title = QLabel(f"Progress Workflow {self.mekanisme}")
        title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        """)
        layout.addWidget(title)

        # Stepper row
        stepper_layout = QHBoxLayout()
        stepper_layout.setContentsMargins(0, 0, 0, 0)
        stepper_layout.setSpacing(0)

        # Get fase names based on mekanisme
        fase_names = self._get_fase_names()

        for i in range(1, 6):
            # Add step
            state = self._get_fase_state(i)
            step = FaseStep(i, fase_names.get(i, f"Fase {i}"), state)
            step.clicked.connect(self._on_step_clicked)
            self._steps[i] = step
            stepper_layout.addWidget(step)

            # Add connector (except after last step)
            if i < 5:
                connector = FaseConnector(completed=(i < self.fase_aktif))
                self._connectors.append(connector)
                stepper_layout.addWidget(connector, alignment=Qt.AlignVCenter)

        layout.addLayout(stepper_layout)

    def _get_fase_names(self) -> Dict[int, str]:
        """Get fase names based on mekanisme."""
        names = {
            "UP": {
                1: "Inisiasi & SK",
                2: "Pencairan UM",
                3: "Pelaksanaan",
                4: "Pertanggungjawaban",
                5: "SPBY & Selesai"
            },
            "TUP": {
                1: "Pengajuan",
                2: "Persetujuan",
                3: "Pencairan",
                4: "Penggunaan",
                5: "Pertanggungjawaban"
            },
            "LS": {
                1: "Kontrak/SPK",
                2: "Pelaksanaan",
                3: "Serah Terima",
                4: "Tagihan SPM",
                5: "SP2D & Selesai"
            }
        }
        return names.get(self.mekanisme, names["UP"])

    def _get_fase_state(self, fase: int) -> str:
        """Get state for a fase number."""
        if fase < self.fase_aktif:
            return "completed"
        elif fase == self.fase_aktif:
            return "active"
        else:
            return "pending"

    def _add_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

    def _on_step_clicked(self, fase: int):
        """Handle step click."""
        self.fase_clicked.emit(fase)

    def set_fase_aktif(self, fase: int):
        """Set the active fase and update all steps."""
        if fase < 1 or fase > 5:
            return

        self.fase_aktif = fase

        # Update all steps
        for i, step in self._steps.items():
            step.set_state(self._get_fase_state(i))

        # Update connectors
        for i, connector in enumerate(self._connectors, start=1):
            connector.set_completed(i < fase)

    def set_fase_state(self, fase: int, state: str):
        """Set specific fase state."""
        if fase in self._steps:
            self._steps[fase].set_state(state)

    def get_step(self, fase: int) -> Optional[FaseStep]:
        """Get step widget by fase number."""
        return self._steps.get(fase)

    def set_mekanisme(self, mekanisme: str):
        """Change mekanisme and update fase names."""
        self.mekanisme = mekanisme.upper()
        fase_names = self._get_fase_names()

        for i, step in self._steps.items():
            step.nama = fase_names.get(i, f"Fase {i}")
            step.label.setText(step.nama)
