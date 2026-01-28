"""
Configuration Package for Asisten PPK Offline
==============================================
Contains workflow configurations for UP, TUP, and LS mechanisms.
"""

from .workflow_config import (
    UP_WORKFLOW,
    TUP_WORKFLOW,
    LS_WORKFLOW,
    ALL_WORKFLOWS,
    get_workflow,
    get_fase_config,
    get_dokumen_list,
)

__all__ = [
    'UP_WORKFLOW',
    'TUP_WORKFLOW',
    'LS_WORKFLOW',
    'ALL_WORKFLOWS',
    'get_workflow',
    'get_fase_config',
    'get_dokumen_list',
]
