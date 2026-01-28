"""
PPK DOCUMENT FACTORY - Services Module
======================================
Business logic services for document generation and workflow management.
"""

from .dokumen_generator import DokumenGenerator, get_dokumen_generator

__all__ = ['DokumenGenerator', 'get_dokumen_generator']
