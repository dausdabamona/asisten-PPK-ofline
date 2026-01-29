"""
PPK DOCUMENT FACTORY - Icon Management
======================================
Centralized icon management system.

Classes:
    IconProvider: Singleton class untuk mengelola icons dengan
                 caching dan fallback mechanism
"""

from app.ui.icons.icon_provider import IconProvider

__all__ = [
    'IconProvider',
]
