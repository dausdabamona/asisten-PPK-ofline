"""
PPK DOCUMENT FACTORY - Dashboard Components
============================================
Komponen-komponen untuk dashboard utama.

Classes:
    StatisticsSection: Section untuk statistik pencairan dana (UP, TUP, LS)
    MekanismeStatCard: Card individual untuk satu mekanisme
    SaldoUPWidget: Widget untuk menampilkan saldo UP
    QuickActionsWidget: Widget untuk tombol aksi cepat
    QuickActionButton: Styled button untuk quick action
    RecentActivityWidget: Widget untuk menampilkan aktivitas/transaksi terbaru
    TransactionItemWidget: Item individual untuk satu transaksi
"""

from app.ui.dashboard_components.statistics_section import (
    StatisticsSection,
    MekanismeStatCard,
)
from app.ui.dashboard_components.saldo_widget import SaldoUPWidget
from app.ui.dashboard_components.quick_actions import (
    QuickActionsWidget,
    QuickActionButton,
)
from app.ui.dashboard_components.recent_activity import (
    RecentActivityWidget,
    TransactionItemWidget,
)

__all__ = [
    'StatisticsSection',
    'MekanismeStatCard',
    'SaldoUPWidget',
    'QuickActionsWidget',
    'QuickActionButton',
    'RecentActivityWidget',
    'TransactionItemWidget',
]
