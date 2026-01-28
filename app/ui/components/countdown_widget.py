"""
Countdown Widget - Untuk menampilkan countdown 30 hari TUP
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QGroupBox
)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QFont, QColor
from datetime import datetime, timedelta


class CountdownWidget(QWidget):
    """Widget untuk menampilkan countdown periode TUP (max 30 hari)"""
    
    def __init__(self, tanggal_sp2d: datetime = None, max_hari: int = 30, parent=None):
        super().__init__(parent)
        self.tanggal_sp2d = tanggal_sp2d or datetime.now()
        self.max_hari = max_hari
        self.tanggal_deadline = self.tanggal_sp2d + timedelta(days=max_hari)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # Update setiap 1 detik
        
        self.setup_ui()
        self.update_countdown()
    
    def setup_ui(self):
        """Setup UI untuk countdown"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Warning box
        warning_group = QGroupBox("⏰ BATAS WAKTU PERTANGGUNGJAWABAN TUP")
        warning_layout = QVBoxLayout()
        warning_layout.setSpacing(15)
        
        # Info tanggal
        info_layout = QHBoxLayout()
        info_layout.setSpacing(30)
        
        # Tanggal SP2D
        sp2d_layout = QVBoxLayout()
        sp2d_layout.setSpacing(5)
        
        label_sp2d = QLabel("📅 Tanggal SP2D Diterima:")
        sp2d_font = QFont()
        sp2d_font.setPointSize(9)
        sp2d_font.setBold(True)
        label_sp2d.setFont(sp2d_font)
        
        self.display_sp2d = QLabel(self.tanggal_sp2d.strftime("%d %B %Y"))
        sp2d_display_font = QFont()
        sp2d_display_font.setPointSize(10)
        self.display_sp2d.setFont(sp2d_display_font)
        self.display_sp2d.setStyleSheet("color: #3498db;")
        
        sp2d_layout.addWidget(label_sp2d)
        sp2d_layout.addWidget(self.display_sp2d)
        info_layout.addLayout(sp2d_layout)
        
        # Deadline
        deadline_layout = QVBoxLayout()
        deadline_layout.setSpacing(5)
        
        label_deadline = QLabel("🔔 Batas Akhir Pertanggungjawaban:")
        deadline_font = QFont()
        deadline_font.setPointSize(9)
        deadline_font.setBold(True)
        label_deadline.setFont(deadline_font)
        
        self.display_deadline = QLabel(self.tanggal_deadline.strftime("%d %B %Y"))
        deadline_display_font = QFont()
        deadline_display_font.setPointSize(10)
        self.display_deadline.setFont(deadline_display_font)
        self.display_deadline.setStyleSheet("color: #e74c3c;")
        
        deadline_layout.addWidget(label_deadline)
        deadline_layout.addWidget(self.display_deadline)
        info_layout.addLayout(deadline_layout)
        
        info_layout.addStretch()
        warning_layout.addLayout(info_layout)
        
        # Progress bar
        progress_label = QLabel("Progress Waktu Tersisa:")
        progress_font = QFont()
        progress_font.setPointSize(9)
        progress_font.setBold(True)
        progress_label.setFont(progress_font)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
            }
        """)
        
        warning_layout.addWidget(progress_label)
        warning_layout.addWidget(self.progress_bar)
        
        # Countdown display
        countdown_label = QLabel("Sisa Waktu:")
        countdown_font = QFont()
        countdown_font.setPointSize(9)
        countdown_font.setBold(True)
        countdown_label.setFont(countdown_font)
        
        countdown_layout = QHBoxLayout()
        countdown_layout.setSpacing(10)
        
        self.display_hari = QLabel("0 Hari")
        hari_font = QFont()
        hari_font.setPointSize(12)
        hari_font.setBold(True)
        self.display_hari.setFont(hari_font)
        self.display_hari.setStyleSheet("color: #e74c3c;")
        
        sep1 = QLabel("|")
        sep1_font = QFont()
        sep1_font.setPointSize(12)
        sep1.setFont(sep1_font)
        
        self.display_jam = QLabel("0 Jam")
        jam_font = QFont()
        jam_font.setPointSize(11)
        jam_font.setBold(True)
        self.display_jam.setFont(jam_font)
        
        sep2 = QLabel("|")
        sep2_font = QFont()
        sep2_font.setPointSize(12)
        sep2.setFont(sep2_font)
        
        self.display_menit = QLabel("0 Menit")
        menit_font = QFont()
        menit_font.setPointSize(11)
        self.display_menit.setFont(menit_font)
        
        countdown_layout.addWidget(self.display_hari)
        countdown_layout.addWidget(sep1)
        countdown_layout.addWidget(self.display_jam)
        countdown_layout.addWidget(sep2)
        countdown_layout.addWidget(self.display_menit)
        countdown_layout.addStretch()
        
        warning_layout.addWidget(countdown_label)
        warning_layout.addLayout(countdown_layout)
        
        # Warning message
        self.warning_message = QLabel()
        warning_msg_font = QFont()
        warning_msg_font.setPointSize(9)
        warning_msg_font.setItalic(True)
        self.warning_message.setFont(warning_msg_font)
        self.warning_message.setWordWrap(True)
        
        warning_layout.addWidget(self.warning_message)
        
        warning_group.setLayout(warning_layout)
        layout.addWidget(warning_group)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_countdown(self):
        """Update countdown display"""
        sekarang = datetime.now()
        sisa = self.tanggal_deadline - sekarang
        
        if sisa.total_seconds() <= 0:
            # Deadline sudah lewat
            self.display_hari.setText("0 Hari")
            self.display_jam.setText("0 Jam")
            self.display_menit.setText("0 Menit")
            
            self.display_hari.setStyleSheet("color: #e74c3c;")
            self.display_jam.setStyleSheet("color: #e74c3c;")
            self.display_menit.setStyleSheet("color: #e74c3c;")
            
            self.progress_bar.setValue(0)
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #e74c3c;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #ffe6e6;
                }
                QProgressBar::chunk {
                    background-color: #e74c3c;
                }
            """)
            
            self.warning_message.setText(
                "⛔ DEADLINE SUDAH LEWAT! Segera selesaikan pertanggungjawaban TUP."
            )
            self.warning_message.setStyleSheet("color: #e74c3c; font-weight: bold;")
        else:
            # Masih dalam batas waktu
            total_sisa_detik = sisa.total_seconds()
            hari = int(total_sisa_detik // 86400)
            jam = int((total_sisa_detik % 86400) // 3600)
            menit = int((total_sisa_detik % 3600) // 60)
            
            self.display_hari.setText(f"{hari} Hari")
            self.display_jam.setText(f"{jam} Jam")
            self.display_menit.setText(f"{menit} Menit")
            
            # Update progress
            total_sisa_hari = total_sisa_detik / 86400
            progress_persen = int((1 - total_sisa_hari / self.max_hari) * 100)
            self.progress_bar.setValue(progress_persen)
            
            # Update warning message & color
            if hari <= 0 and jam <= 24:
                # Kurang dari 1 hari
                self.display_hari.setStyleSheet("color: #e74c3c;")
                self.display_jam.setStyleSheet("color: #e74c3c;")
                self.display_menit.setStyleSheet("color: #e74c3c;")
                
                self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid #e74c3c;
                        border-radius: 5px;
                        text-align: center;
                        background-color: #ffe6e6;
                    }
                    QProgressBar::chunk {
                        background-color: #e74c3c;
                    }
                """)
                
                self.warning_message.setText(
                    f"⚠️ URGENT! Hanya tinggal {jam} jam {menit} menit lagi. "
                    "Segera selesaikan pertanggungjawaban TUP!"
                )
                self.warning_message.setStyleSheet("color: #e74c3c; font-weight: bold;")
            
            elif hari <= 5:
                # Kurang dari 5 hari
                self.display_hari.setStyleSheet("color: #f39c12;")
                self.display_jam.setStyleSheet("color: #95a5a6;")
                self.display_menit.setStyleSheet("color: #95a5a6;")
                
                self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid #f39c12;
                        border-radius: 5px;
                        text-align: center;
                        background-color: #fff3cd;
                    }
                    QProgressBar::chunk {
                        background-color: #f39c12;
                    }
                """)
                
                self.warning_message.setText(
                    f"⚠️ Perhatian! Sisa waktu {hari} hari. "
                    "Pastikan pertanggungjawaban TUP selesai tepat waktu."
                )
                self.warning_message.setStyleSheet("color: #f39c12;")
            
            else:
                # Masih banyak waktu
                self.display_hari.setStyleSheet("color: #27ae60;")
                self.display_jam.setStyleSheet("color: #95a5a6;")
                self.display_menit.setStyleSheet("color: #95a5a6;")
                
                self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid #bdc3c7;
                        border-radius: 5px;
                        text-align: center;
                        background-color: #ecf0f1;
                    }
                    QProgressBar::chunk {
                        background-color: #27ae60;
                    }
                """)
                
                self.warning_message.setText(
                    "✓ Waktu masih cukup. Lanjutkan pertanggungjawaban TUP dengan tertib."
                )
                self.warning_message.setStyleSheet("color: #27ae60;")
    
    def set_tanggal_sp2d(self, tanggal: datetime):
        """Set tanggal SP2D"""
        self.tanggal_sp2d = tanggal
        self.tanggal_deadline = self.tanggal_sp2d + timedelta(days=self.max_hari)
        
        self.display_sp2d.setText(self.tanggal_sp2d.strftime("%d %B %Y"))
        self.display_deadline.setText(self.tanggal_deadline.strftime("%d %B %Y"))
        
        self.update_countdown()
