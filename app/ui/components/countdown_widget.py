"""
PPK DOCUMENT FACTORY - Countdown Widget Component
==================================================
Widget untuk menampilkan countdown waktu TUP.
TUP harus selesai dalam 1 bulan (30 hari) sejak SP2D.

Features:
- Display sisa hari
- Visual indicator (safe, warning, danger)
- Progress bar
- Tanggal SP2D dan batas waktu
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QProgressBar,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont

from datetime import datetime, date, timedelta
from typing import Optional


class CountdownWidget(QFrame):
    """
    Widget untuk countdown TUP.

    Signals:
        deadline_reached(): Emitted when countdown reaches 0
        warning_triggered(): Emitted when countdown enters warning zone
    """

    deadline_reached = Signal()
    warning_triggered = Signal()

    BATAS_TUP_HARI = 30

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tanggal_sp2d: Optional[date] = None
        self._batas_waktu: Optional[date] = None
        self._is_running = False

        self._setup_ui()
        self._add_shadow()

        # Timer for auto-update (every minute)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_display)

    def _setup_ui(self):
        """Setup widget UI."""
        self.setObjectName("countdownWidget")
        self.setStyleSheet("""
            #countdownWidget {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #ecf0f1;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Batas Waktu TUP")
        title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Status badge
        self.status_badge = QLabel("Menunggu SP2D")
        self.status_badge.setStyleSheet("""
            background-color: #bdc3c7;
            color: white;
            border-radius: 10px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 500;
        """)
        header_layout.addWidget(self.status_badge)

        main_layout.addLayout(header_layout)

        # Countdown value
        self.countdown_label = QLabel("--")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("""
            font-size: 64px;
            font-weight: bold;
            color: #bdc3c7;
        """)
        main_layout.addWidget(self.countdown_label)

        # Days label
        self.days_label = QLabel("hari tersisa")
        self.days_label.setAlignment(Qt.AlignCenter)
        self.days_label.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            margin-top: -10px;
        """)
        main_layout.addWidget(self.days_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.BATAS_TUP_HARI)
        self.progress_bar.setValue(self.BATAS_TUP_HARI)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #ecf0f1;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #bdc3c7;
                border-radius: 4px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Dates info
        dates_layout = QHBoxLayout()

        # SP2D date
        sp2d_layout = QVBoxLayout()
        sp2d_layout.setSpacing(2)

        sp2d_title = QLabel("Tanggal SP2D")
        sp2d_title.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        sp2d_layout.addWidget(sp2d_title)

        self.sp2d_label = QLabel("-")
        self.sp2d_label.setStyleSheet("font-size: 12px; color: #2c3e50; font-weight: 500;")
        sp2d_layout.addWidget(self.sp2d_label)

        dates_layout.addLayout(sp2d_layout)

        dates_layout.addStretch()

        # Deadline date
        deadline_layout = QVBoxLayout()
        deadline_layout.setSpacing(2)
        deadline_layout.setAlignment(Qt.AlignRight)

        deadline_title = QLabel("Batas Waktu")
        deadline_title.setAlignment(Qt.AlignRight)
        deadline_title.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        deadline_layout.addWidget(deadline_title)

        self.deadline_label = QLabel("-")
        self.deadline_label.setAlignment(Qt.AlignRight)
        self.deadline_label.setStyleSheet("font-size: 12px; color: #2c3e50; font-weight: 500;")
        deadline_layout.addWidget(self.deadline_label)

        dates_layout.addLayout(deadline_layout)

        main_layout.addLayout(dates_layout)

        # Warning message
        self.warning_label = QLabel("")
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("""
            font-size: 11px;
            color: #7f8c8d;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
            margin-top: 5px;
        """)
        self.warning_label.hide()
        main_layout.addWidget(self.warning_label)

    def _add_shadow(self):
        """Add drop shadow effect."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

    def _format_date(self, d: date) -> str:
        """Format date to Indonesian format."""
        months = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        return f"{d.day} {months[d.month - 1]} {d.year}"

    def _update_display(self):
        """Update countdown display."""
        if not self._tanggal_sp2d or not self._batas_waktu:
            return

        today = date.today()
        sisa_hari = (self._batas_waktu - today).days

        # Update countdown value
        self.countdown_label.setText(str(max(0, sisa_hari)))

        # Update progress bar
        self.progress_bar.setValue(max(0, sisa_hari))

        # Determine state and update styling
        if sisa_hari < 0:
            # Overdue
            self._set_state("overdue", abs(sisa_hari))
        elif sisa_hari <= 5:
            # Danger zone
            self._set_state("danger", sisa_hari)
        elif sisa_hari <= 10:
            # Warning zone
            self._set_state("warning", sisa_hari)
            self.warning_triggered.emit()
        else:
            # Safe
            self._set_state("safe", sisa_hari)

        # Check deadline
        if sisa_hari == 0:
            self.deadline_reached.emit()

    def _set_state(self, state: str, sisa_hari: int):
        """Set widget state and update styling."""
        states = {
            "safe": {
                "color": "#27ae60",
                "badge_bg": "#27ae60",
                "badge_text": "Aman",
                "progress_color": "#27ae60",
            },
            "warning": {
                "color": "#f39c12",
                "badge_bg": "#f39c12",
                "badge_text": "Perhatian",
                "progress_color": "#f39c12",
            },
            "danger": {
                "color": "#e74c3c",
                "badge_bg": "#e74c3c",
                "badge_text": "Segera!",
                "progress_color": "#e74c3c",
            },
            "overdue": {
                "color": "#c0392b",
                "badge_bg": "#c0392b",
                "badge_text": "TERLAMBAT",
                "progress_color": "#c0392b",
            }
        }

        s = states.get(state, states["safe"])

        # Update countdown label
        self.countdown_label.setStyleSheet(f"""
            font-size: 64px;
            font-weight: bold;
            color: {s['color']};
        """)

        # Update status badge
        self.status_badge.setText(s['badge_text'])
        self.status_badge.setStyleSheet(f"""
            background-color: {s['badge_bg']};
            color: white;
            border-radius: 10px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 500;
        """)

        # Update progress bar
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #ecf0f1;
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {s['progress_color']};
                border-radius: 4px;
            }}
        """)

        # Update days label
        if state == "overdue":
            self.days_label.setText("hari terlambat!")
            self.countdown_label.setText(str(abs(sisa_hari)))
        else:
            self.days_label.setText("hari tersisa")

        # Show/update warning message
        if state == "overdue":
            self.warning_label.setText(
                "TUP sudah melewati batas waktu! Segera selesaikan pertanggungjawaban "
                "dan kembalikan sisa dana ke kas negara."
            )
            self.warning_label.setStyleSheet("""
                font-size: 11px;
                color: #c0392b;
                padding: 10px;
                background-color: #fdeaea;
                border-radius: 5px;
                margin-top: 5px;
                border: 1px solid #e74c3c;
            """)
            self.warning_label.show()
        elif state == "danger":
            self.warning_label.setText(
                f"Hanya tersisa {sisa_hari} hari untuk menyelesaikan TUP. "
                "Segera selesaikan semua transaksi!"
            )
            self.warning_label.setStyleSheet("""
                font-size: 11px;
                color: #943126;
                padding: 10px;
                background-color: #fdeaea;
                border-radius: 5px;
                margin-top: 5px;
            """)
            self.warning_label.show()
        elif state == "warning":
            self.warning_label.setText(
                f"Tersisa {sisa_hari} hari. Pastikan semua transaksi selesai tepat waktu."
            )
            self.warning_label.setStyleSheet("""
                font-size: 11px;
                color: #9a7d0a;
                padding: 10px;
                background-color: #fef5e7;
                border-radius: 5px;
                margin-top: 5px;
            """)
            self.warning_label.show()
        else:
            self.warning_label.hide()

    def set_tanggal_sp2d(self, tanggal: date):
        """Set tanggal SP2D dan hitung batas waktu."""
        if isinstance(tanggal, str):
            tanggal = datetime.strptime(tanggal, '%Y-%m-%d').date()

        self._tanggal_sp2d = tanggal
        self._batas_waktu = tanggal + timedelta(days=self.BATAS_TUP_HARI)

        # Update date labels
        self.sp2d_label.setText(self._format_date(self._tanggal_sp2d))
        self.deadline_label.setText(self._format_date(self._batas_waktu))

        # Update display
        self._update_display()

        # Start timer
        self._start_timer()

    def _start_timer(self):
        """Start auto-update timer."""
        if not self._is_running:
            self._timer.start(60000)  # Update every minute
            self._is_running = True

    def stop(self):
        """Stop auto-update timer."""
        self._timer.stop()
        self._is_running = False

    def get_sisa_hari(self) -> int:
        """Get remaining days."""
        if not self._batas_waktu:
            return -1

        today = date.today()
        return (self._batas_waktu - today).days

    def is_overdue(self) -> bool:
        """Check if TUP is overdue."""
        return self.get_sisa_hari() < 0

    def reset(self):
        """Reset countdown."""
        self._tanggal_sp2d = None
        self._batas_waktu = None
        self.stop()

        self.countdown_label.setText("--")
        self.countdown_label.setStyleSheet("""
            font-size: 64px;
            font-weight: bold;
            color: #bdc3c7;
        """)
        self.days_label.setText("hari tersisa")
        self.sp2d_label.setText("-")
        self.deadline_label.setText("-")
        self.status_badge.setText("Menunggu SP2D")
        self.status_badge.setStyleSheet("""
            background-color: #bdc3c7;
            color: white;
            border-radius: 10px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 500;
        """)
        self.progress_bar.setValue(self.BATAS_TUP_HARI)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #ecf0f1;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #bdc3c7;
                border-radius: 4px;
            }
        """)
        self.warning_label.hide()
