"""
PPK DOCUMENT FACTORY - UP Detail Page
======================================
Detail page for Uang Persediaan (UP) transactions.
"""

from .base_detail_page import BaseDetailPage


class UPDetailPage(BaseDetailPage):
    """Detail page for UP transactions."""

    MEKANISME = "UP"
    COLOR = "#27ae60"
