"""
PPK DOCUMENT FACTORY - Workflow Analytics Widget
=================================================
Analytics widget untuk insights workflow.

Features:
- WorkflowMetrics: Data class untuk metrics
- MetricCard: Single metric display
- WorkflowAnalyticsWidget: Dashboard analytics
- BottleneckAlert: Highlight bottleneck fase

Author: PPK Document Factory Team
Version: 4.0
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
    QComboBox, QGridLayout, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QTimer, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QPainterPath


# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

# Fase names
FASE_NAMES = {
    1: "Inisiasi",
    2: "Pencairan UM",
    3: "Pelaksanaan",
    4: "Pertanggungjawaban",
    5: "SPBY & Selesai"
}

# Metric colors
METRIC_COLORS = {
    "good": {"bg": "#e8f5e9", "text": "#2e7d32", "icon": "#4caf50"},
    "warning": {"bg": "#fff3e0", "text": "#e65100", "icon": "#ff9800"},
    "bad": {"bg": "#ffebee", "text": "#c62828", "icon": "#f44336"},
    "neutral": {"bg": "#e3f2fd", "text": "#1565c0", "icon": "#2196f3"},
}

# Trend icons
TREND_UP = "\u2191"    # ↑
TREND_DOWN = "\u2193"  # ↓
TREND_FLAT = "\u2192"  # →


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class WorkflowMetrics:
    """
    Data class containing workflow metrics.

    Attributes:
        avg_completion_time: Average time to complete a transaksi
        avg_time_per_fase: Average time spent in each fase
        bottleneck_fase: Fase with longest average time
        completion_rate: Percentage of transaksi completed
        overdue_count: Number of overdue transaksi
        on_track_count: Number of transaksi on track
        total_count: Total number of transaksi
        total_nilai: Total nilai of all transaksi
    """
    avg_completion_time: timedelta = field(default_factory=lambda: timedelta(days=0))
    avg_time_per_fase: Dict[int, timedelta] = field(default_factory=dict)
    bottleneck_fase: Optional[int] = None
    completion_rate: float = 0.0
    overdue_count: int = 0
    on_track_count: int = 0
    total_count: int = 0
    total_nilai: float = 0.0

    def get_bottleneck_name(self) -> str:
        """Get name of bottleneck fase."""
        if self.bottleneck_fase:
            return FASE_NAMES.get(self.bottleneck_fase, f"Fase {self.bottleneck_fase}")
        return "N/A"

    def format_avg_completion(self) -> str:
        """Format average completion time."""
        days = self.avg_completion_time.days
        if days == 0:
            hours = self.avg_completion_time.seconds // 3600
            return f"{hours} jam"
        return f"{days} hari"

    def format_completion_rate(self) -> str:
        """Format completion rate as percentage."""
        return f"{self.completion_rate:.0f}%"


# =============================================================================
# METRIC CARD
# =============================================================================

class MetricCard(QFrame):
    """
    Single metric display card.

    Features:
    - Large value display
    - Label description
    - Trend indicator (optional)
    - Color based on status

    Signals:
        clicked(): Emit when card is clicked
    """

    clicked = Signal()

    def __init__(
        self,
        value: str,
        label: str,
        icon: str = "",
        trend: Optional[str] = None,
        trend_value: Optional[str] = None,
        status: str = "neutral",
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.value = value
        self.label = label
        self.icon = icon
        self.trend = trend
        self.trend_value = trend_value
        self.status = status

        self._setup_ui()
        self._apply_style()
        self._setup_shadow()

    def _setup_ui(self):
        """Setup card UI."""
        self.setFixedSize(160, 100)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # Icon + Value row
        value_layout = QHBoxLayout()
        value_layout.setSpacing(8)

        if self.icon:
            self.icon_label = QLabel(self.icon)
            self.icon_label.setFont(QFont("Segoe UI", 16))
            value_layout.addWidget(self.icon_label)

        self.value_label = QLabel(self.value)
        self.value_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        value_layout.addWidget(self.value_label)

        value_layout.addStretch()

        # Trend indicator
        if self.trend:
            trend_text = self.trend
            if self.trend_value:
                trend_text = f"{self.trend} {self.trend_value}"

            self.trend_label = QLabel(trend_text)
            self.trend_label.setFont(QFont("Segoe UI", 10, QFont.Bold))

            if self.trend == TREND_UP:
                self.trend_label.setStyleSheet("color: #4caf50;")
            elif self.trend == TREND_DOWN:
                self.trend_label.setStyleSheet("color: #f44336;")
            else:
                self.trend_label.setStyleSheet("color: #757575;")

            value_layout.addWidget(self.trend_label)

        layout.addLayout(value_layout)

        # Label
        self.label_widget = QLabel(self.label)
        self.label_widget.setFont(QFont("Segoe UI", 9))
        self.label_widget.setWordWrap(True)
        layout.addWidget(self.label_widget)

        layout.addStretch()

    def _apply_style(self):
        """Apply styling based on status."""
        colors = METRIC_COLORS.get(self.status, METRIC_COLORS["neutral"])

        self.setStyleSheet(f"""
            MetricCard {{
                background-color: {colors['bg']};
                border: 1px solid {colors['bg']};
                border-radius: 8px;
            }}
            MetricCard:hover {{
                border: 1px solid {colors['icon']};
            }}
        """)

        self.value_label.setStyleSheet(f"color: {colors['text']};")
        self.label_widget.setStyleSheet(f"color: {colors['text']}; opacity: 0.8;")

        if hasattr(self, 'icon_label'):
            self.icon_label.setStyleSheet(f"color: {colors['icon']};")

    def _setup_shadow(self):
        """Add subtle shadow."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(6)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def mousePressEvent(self, event):
        """Handle click."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def update_value(self, value: str, status: Optional[str] = None):
        """Update the displayed value."""
        self.value = value
        self.value_label.setText(value)
        if status:
            self.status = status
            self._apply_style()

    def update_trend(self, trend: str, trend_value: Optional[str] = None):
        """Update the trend indicator."""
        self.trend = trend
        self.trend_value = trend_value
        if hasattr(self, 'trend_label'):
            text = trend
            if trend_value:
                text = f"{trend} {trend_value}"
            self.trend_label.setText(text)

            if trend == TREND_UP:
                self.trend_label.setStyleSheet("color: #4caf50;")
            elif trend == TREND_DOWN:
                self.trend_label.setStyleSheet("color: #f44336;")
            else:
                self.trend_label.setStyleSheet("color: #757575;")


# =============================================================================
# FASE BAR CHART
# =============================================================================

class FaseBarChart(QWidget):
    """
    Simple horizontal bar chart showing time per fase.

    Features:
    - Bar for each fase
    - Bottleneck highlighting
    - Value labels
    """

    fase_clicked = Signal(int)

    def __init__(
        self,
        data: Optional[Dict[int, float]] = None,
        bottleneck: Optional[int] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.data = data or {}
        self.bottleneck = bottleneck
        self.setMinimumHeight(180)

    def set_data(self, data: Dict[int, float], bottleneck: Optional[int] = None):
        """Set chart data."""
        self.data = data
        self.bottleneck = bottleneck
        self.update()

    def paintEvent(self, event):
        """Paint the bar chart."""
        super().paintEvent(event)

        if not self.data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        margin_left = 120
        margin_right = 80
        margin_top = 10
        margin_bottom = 10
        bar_height = 24
        bar_spacing = 12

        # Calculate max value for scaling
        max_value = max(self.data.values()) if self.data else 1
        usable_width = width - margin_left - margin_right

        y = margin_top
        for fase in range(1, 6):
            value = self.data.get(fase, 0)
            fase_name = FASE_NAMES.get(fase, f"Fase {fase}")

            # Draw fase label
            painter.setPen(QPen(QColor("#424242")))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(10, y + bar_height - 6, f"Fase {fase}")

            # Draw bar
            bar_width = (value / max_value) * usable_width if max_value > 0 else 0

            if fase == self.bottleneck:
                # Bottleneck bar - red/orange
                painter.setBrush(QBrush(QColor("#ff5722")))
                painter.setPen(QPen(QColor("#e64a19"), 1))
            else:
                # Normal bar - blue
                painter.setBrush(QBrush(QColor("#2196f3")))
                painter.setPen(QPen(QColor("#1976d2"), 1))

            bar_rect = QRectF(margin_left, y, bar_width, bar_height)
            painter.drawRoundedRect(bar_rect, 4, 4)

            # Draw value label
            painter.setPen(QPen(QColor("#424242")))
            painter.setFont(QFont("Segoe UI", 9))
            value_text = f"{value:.1f} hari"
            painter.drawText(int(margin_left + bar_width + 8), y + bar_height - 6, value_text)

            # Draw bottleneck indicator
            if fase == self.bottleneck:
                painter.setPen(QPen(QColor("#e64a19")))
                painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
                painter.drawText(width - 70, y + bar_height - 6, "\u2190 Bottleneck")

            y += bar_height + bar_spacing

        painter.end()

    def mousePressEvent(self, event):
        """Handle click on a bar."""
        if event.button() == Qt.LeftButton:
            margin_top = 10
            bar_height = 24
            bar_spacing = 12

            click_y = event.pos().y()
            for fase in range(1, 6):
                bar_y = margin_top + (fase - 1) * (bar_height + bar_spacing)
                if bar_y <= click_y <= bar_y + bar_height:
                    self.fase_clicked.emit(fase)
                    break

        super().mousePressEvent(event)


# =============================================================================
# TREND LINE CHART
# =============================================================================

class TrendLineChart(QWidget):
    """
    Simple line chart showing weekly completion trend.

    Features:
    - Line plot of completions over time
    - Hover tooltips
    - Grid lines
    """

    def __init__(
        self,
        data: Optional[List[Tuple[str, int]]] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.data = data or []
        self.setMinimumHeight(120)

    def set_data(self, data: List[Tuple[str, int]]):
        """Set chart data as list of (label, value) tuples."""
        self.data = data
        self.update()

    def paintEvent(self, event):
        """Paint the line chart."""
        super().paintEvent(event)

        if not self.data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        margin = 40
        chart_width = width - (2 * margin)
        chart_height = height - (2 * margin)

        # Calculate max value
        max_value = max(v for _, v in self.data) if self.data else 1
        if max_value == 0:
            max_value = 1

        # Draw grid lines
        painter.setPen(QPen(QColor("#eeeeee"), 1, Qt.DashLine))
        for i in range(5):
            y = margin + (chart_height / 4) * i
            painter.drawLine(margin, int(y), width - margin, int(y))

        # Calculate points
        points = []
        step_x = chart_width / (len(self.data) - 1) if len(self.data) > 1 else chart_width
        for i, (label, value) in enumerate(self.data):
            x = margin + (step_x * i)
            y = margin + chart_height - (value / max_value * chart_height)
            points.append((x, y, label, value))

        # Draw line
        if len(points) > 1:
            painter.setPen(QPen(QColor("#2196f3"), 2))
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            for x, y, _, _ in points[1:]:
                path.lineTo(x, y)
            painter.drawPath(path)

        # Draw points and labels
        for x, y, label, value in points:
            # Point
            painter.setBrush(QBrush(QColor("#2196f3")))
            painter.setPen(QPen(QColor("#1565c0"), 2))
            painter.drawEllipse(int(x - 4), int(y - 4), 8, 8)

            # X-axis label
            painter.setPen(QPen(QColor("#757575")))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(int(x - 15), height - 10, label)

        painter.end()


# =============================================================================
# BOTTLENECK ALERT
# =============================================================================

class BottleneckAlert(QFrame):
    """
    Alert widget highlighting bottleneck fase.

    Features:
    - Prominent display of bottleneck
    - Suggestion for improvement
    - Link to stuck transaksi
    """

    view_stuck_clicked = Signal(int)

    def __init__(
        self,
        fase: int,
        avg_time: float,
        stuck_count: int = 0,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.fase = fase
        self.avg_time = avg_time
        self.stuck_count = stuck_count

        self._setup_ui()

    def _setup_ui(self):
        """Setup alert UI."""
        self.setStyleSheet("""
            BottleneckAlert {
                background-color: #fff3e0;
                border: 1px solid #ffb74d;
                border-left: 4px solid #ff9800;
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()

        icon_label = QLabel("\u26A0\uFE0F")
        icon_label.setFont(QFont("Segoe UI", 14))
        header_layout.addWidget(icon_label)

        title_label = QLabel("Bottleneck Terdeteksi")
        title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title_label.setStyleSheet("color: #e65100;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Description
        fase_name = FASE_NAMES.get(self.fase, f"Fase {self.fase}")
        desc_text = f"Fase {self.fase} ({fase_name}) memiliki rata-rata waktu {self.avg_time:.1f} hari, " \
                    f"lebih lama dari fase lainnya."
        desc_label = QLabel(desc_text)
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #424242;")
        layout.addWidget(desc_label)

        # Suggestion
        suggestion_label = QLabel("\U0001F4A1 Saran: Periksa transaksi yang stuck di fase ini dan identifikasi hambatan.")
        suggestion_label.setFont(QFont("Segoe UI", 9))
        suggestion_label.setWordWrap(True)
        suggestion_label.setStyleSheet("color: #616161;")
        layout.addWidget(suggestion_label)

        # Action button
        if self.stuck_count > 0:
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()

            self.view_btn = QPushButton(f"Lihat {self.stuck_count} Transaksi Stuck")
            self.view_btn.setCursor(Qt.PointingHandCursor)
            self.view_btn.clicked.connect(lambda: self.view_stuck_clicked.emit(self.fase))
            self.view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff9800;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f57c00;
                }
            """)
            btn_layout.addWidget(self.view_btn)

            layout.addLayout(btn_layout)

    def update_data(self, fase: int, avg_time: float, stuck_count: int):
        """Update alert data."""
        self.fase = fase
        self.avg_time = avg_time
        self.stuck_count = stuck_count
        # Rebuild UI
        # Note: In production, update individual labels instead


# =============================================================================
# WORKFLOW ANALYTICS WIDGET
# =============================================================================

class WorkflowAnalyticsWidget(QWidget):
    """
    Dashboard widget for workflow analytics.

    Features:
    - Key metrics display
    - Time per fase chart
    - Trend chart
    - Bottleneck alert

    Signals:
        metric_clicked(str): Emit metric name when clicked
        fase_selected(int): Emit when a fase is selected
        period_changed(str): Emit when period filter changes
    """

    metric_clicked = Signal(str)
    fase_selected = Signal(int)
    period_changed = Signal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self._metrics: Optional[WorkflowMetrics] = None
        self._transaksi_list: List[Dict[str, Any]] = []
        self._period = "Bulan Ini"
        self._mekanisme = "Semua"

        self._setup_ui()

    def _setup_ui(self):
        """Setup analytics UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # ----- Header -----
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)

        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)

        icon_label = QLabel("\U0001F4CA")
        icon_label.setFont(QFont("Segoe UI", 16))
        title_layout.addWidget(icon_label)

        title_label = QLabel("Workflow Analytics")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title_label.setStyleSheet("color: #212121;")
        title_layout.addWidget(title_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Period filter
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Hari Ini", "Minggu Ini", "Bulan Ini", "Tahun Ini", "Semua"])
        self.period_combo.setCurrentText("Bulan Ini")
        self.period_combo.setFixedWidth(120)
        self.period_combo.currentTextChanged.connect(self._on_period_changed)
        self.period_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
            }
        """)
        header_layout.addWidget(self.period_combo)

        layout.addWidget(header)

        # ----- Metrics Cards -----
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        metrics_layout = QHBoxLayout(metrics_frame)
        metrics_layout.setContentsMargins(16, 16, 16, 16)
        metrics_layout.setSpacing(16)

        self.time_card = MetricCard(
            value="- hari",
            label="Rata-rata Waktu",
            icon="\u23F1\uFE0F",
            status="neutral"
        )
        self.time_card.clicked.connect(lambda: self.metric_clicked.emit("avg_time"))
        metrics_layout.addWidget(self.time_card)

        self.rate_card = MetricCard(
            value="-%",
            label="Completion Rate",
            icon="\u2705",
            status="neutral"
        )
        self.rate_card.clicked.connect(lambda: self.metric_clicked.emit("completion_rate"))
        metrics_layout.addWidget(self.rate_card)

        self.overdue_card = MetricCard(
            value="-",
            label="Overdue",
            icon="\u26A0\uFE0F",
            status="neutral"
        )
        self.overdue_card.clicked.connect(lambda: self.metric_clicked.emit("overdue"))
        metrics_layout.addWidget(self.overdue_card)

        self.total_card = MetricCard(
            value="-",
            label="Total Transaksi",
            icon="\U0001F4C8",
            status="neutral"
        )
        self.total_card.clicked.connect(lambda: self.metric_clicked.emit("total"))
        metrics_layout.addWidget(self.total_card)

        metrics_layout.addStretch()

        layout.addWidget(metrics_frame)

        # ----- Charts Section -----
        charts_frame = QFrame()
        charts_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        charts_layout = QVBoxLayout(charts_frame)
        charts_layout.setContentsMargins(16, 16, 16, 16)
        charts_layout.setSpacing(16)

        # Fase bar chart
        fase_header = QLabel("Waktu per Fase:")
        fase_header.setFont(QFont("Segoe UI", 11, QFont.Bold))
        fase_header.setStyleSheet("color: #424242;")
        charts_layout.addWidget(fase_header)

        self.fase_chart = FaseBarChart()
        self.fase_chart.fase_clicked.connect(self.fase_selected.emit)
        charts_layout.addWidget(self.fase_chart)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #e0e0e0;")
        separator.setFixedHeight(1)
        charts_layout.addWidget(separator)

        # Trend chart
        trend_header = QLabel("Trend Mingguan:")
        trend_header.setFont(QFont("Segoe UI", 11, QFont.Bold))
        trend_header.setStyleSheet("color: #424242;")
        charts_layout.addWidget(trend_header)

        self.trend_chart = TrendLineChart()
        charts_layout.addWidget(self.trend_chart)

        layout.addWidget(charts_frame)

        # ----- Bottleneck Alert (initially hidden) -----
        self.bottleneck_alert = BottleneckAlert(fase=1, avg_time=0)
        self.bottleneck_alert.view_stuck_clicked.connect(self.fase_selected.emit)
        self.bottleneck_alert.setVisible(False)
        layout.addWidget(self.bottleneck_alert)

        layout.addStretch()

    def _on_period_changed(self, period: str):
        """Handle period filter change."""
        self._period = period
        self.period_changed.emit(period)
        self.refresh()

    # -------------------------------------------------------------------------
    # Public Methods
    # -------------------------------------------------------------------------

    def calculate_metrics(self, transaksi_list: List[Dict[str, Any]]) -> WorkflowMetrics:
        """
        Calculate workflow metrics from transaksi list.

        Args:
            transaksi_list: List of transaksi dictionaries

        Returns:
            WorkflowMetrics instance
        """
        if not transaksi_list:
            return WorkflowMetrics()

        total_count = len(transaksi_list)
        completed_count = sum(1 for t in transaksi_list if t.get("status") == "Selesai")
        overdue_count = sum(1 for t in transaksi_list if t.get("is_overdue", False))
        on_track_count = total_count - overdue_count
        total_nilai = sum(t.get("nilai", 0) for t in transaksi_list)

        # Calculate completion rate
        completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0

        # Calculate average completion time (for completed transaksi)
        completion_times = []
        for t in transaksi_list:
            if t.get("status") == "Selesai" and t.get("created_at") and t.get("completed_at"):
                created = t["created_at"]
                completed = t["completed_at"]
                if isinstance(created, str):
                    created = datetime.fromisoformat(created)
                if isinstance(completed, str):
                    completed = datetime.fromisoformat(completed)
                completion_times.append(completed - created)

        avg_completion = timedelta(days=0)
        if completion_times:
            total_seconds = sum(t.total_seconds() for t in completion_times)
            avg_completion = timedelta(seconds=total_seconds / len(completion_times))

        # Calculate time per fase
        fase_times: Dict[int, List[float]] = {i: [] for i in range(1, 6)}
        for t in transaksi_list:
            fase_history = t.get("fase_history", [])
            for entry in fase_history:
                fase = entry.get("fase")
                duration = entry.get("duration_days", 0)
                if fase and fase in fase_times:
                    fase_times[fase].append(duration)

        avg_time_per_fase = {}
        for fase, times in fase_times.items():
            if times:
                avg_time_per_fase[fase] = timedelta(days=sum(times) / len(times))
            else:
                avg_time_per_fase[fase] = timedelta(days=0)

        # Find bottleneck
        bottleneck = None
        max_time = timedelta(days=0)
        for fase, time in avg_time_per_fase.items():
            if time > max_time:
                max_time = time
                bottleneck = fase

        return WorkflowMetrics(
            avg_completion_time=avg_completion,
            avg_time_per_fase=avg_time_per_fase,
            bottleneck_fase=bottleneck,
            completion_rate=completion_rate,
            overdue_count=overdue_count,
            on_track_count=on_track_count,
            total_count=total_count,
            total_nilai=total_nilai
        )

    def set_data(self, transaksi_list: List[Dict[str, Any]]):
        """Set transaksi data and calculate metrics."""
        self._transaksi_list = transaksi_list
        self._metrics = self.calculate_metrics(transaksi_list)
        self._update_display()

    def set_metrics(self, metrics: WorkflowMetrics):
        """Directly set metrics."""
        self._metrics = metrics
        self._update_display()

    def set_period(self, start: date, end: date):
        """Set date range for analysis."""
        # Filter transaksi by date
        filtered = []
        for t in self._transaksi_list:
            created = t.get("created_at")
            if created:
                if isinstance(created, str):
                    created = datetime.fromisoformat(created).date()
                elif isinstance(created, datetime):
                    created = created.date()

                if start <= created <= end:
                    filtered.append(t)

        self._metrics = self.calculate_metrics(filtered)
        self._update_display()

    def set_mekanisme(self, mekanisme: str):
        """Set mekanisme filter."""
        self._mekanisme = mekanisme
        self.refresh()

    def refresh(self):
        """Refresh analytics display."""
        filtered = self._transaksi_list

        # Apply mekanisme filter
        if self._mekanisme != "Semua":
            filtered = [t for t in filtered if t.get("mekanisme") == self._mekanisme]

        self._metrics = self.calculate_metrics(filtered)
        self._update_display()

    def _update_display(self):
        """Update all display elements from metrics."""
        if not self._metrics:
            return

        m = self._metrics

        # Update metric cards
        avg_days = m.avg_completion_time.days
        self.time_card.update_value(
            f"{avg_days} hari" if avg_days > 0 else "< 1 hari",
            "good" if avg_days < 14 else "warning" if avg_days < 30 else "bad"
        )

        self.rate_card.update_value(
            f"{m.completion_rate:.0f}%",
            "good" if m.completion_rate >= 80 else "warning" if m.completion_rate >= 50 else "bad"
        )

        self.overdue_card.update_value(
            str(m.overdue_count),
            "good" if m.overdue_count == 0 else "warning" if m.overdue_count < 5 else "bad"
        )

        self.total_card.update_value(
            str(m.total_count),
            "neutral"
        )

        # Update fase chart
        fase_data = {
            fase: time.days + time.seconds / 86400
            for fase, time in m.avg_time_per_fase.items()
        }
        self.fase_chart.set_data(fase_data, m.bottleneck_fase)

        # Update bottleneck alert
        if m.bottleneck_fase and m.avg_time_per_fase.get(m.bottleneck_fase):
            bottleneck_time = m.avg_time_per_fase[m.bottleneck_fase]
            stuck_count = sum(
                1 for t in self._transaksi_list
                if t.get("fase") == m.bottleneck_fase
            )
            self.bottleneck_alert.update_data(
                m.bottleneck_fase,
                bottleneck_time.days + bottleneck_time.seconds / 86400,
                stuck_count
            )
            self.bottleneck_alert.setVisible(True)
        else:
            self.bottleneck_alert.setVisible(False)

    def set_trend_data(self, data: List[Tuple[str, int]]):
        """Set weekly trend data."""
        self.trend_chart.set_data(data)

    def get_metrics(self) -> Optional[WorkflowMetrics]:
        """Get current metrics."""
        return self._metrics


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_analytics_widget(
    transaksi_list: Optional[List[Dict[str, Any]]] = None,
    parent: Optional[QWidget] = None
) -> WorkflowAnalyticsWidget:
    """
    Factory function to create a WorkflowAnalyticsWidget.

    Args:
        transaksi_list: Initial transaksi data
        parent: Parent widget

    Returns:
        Configured WorkflowAnalyticsWidget instance
    """
    widget = WorkflowAnalyticsWidget(parent=parent)

    if transaksi_list:
        widget.set_data(transaksi_list)

    return widget
