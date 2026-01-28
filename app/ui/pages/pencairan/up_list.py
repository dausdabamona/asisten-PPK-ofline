"""
PPK DOCUMENT FACTORY - UP List Page
====================================
List page for Uang Persediaan (UP) transactions.
"""

from .base_list_page import BaseListPage


class UPListPage(BaseListPage):
    """List page for UP transactions."""

    MEKANISME = "UP"
    TITLE = "Uang Persediaan (UP)"
    COLOR = "#27ae60"

    def _get_icon(self) -> str:
        return "W"  # Wallet icon placeholder
