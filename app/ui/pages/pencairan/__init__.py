"""
Pencairan Pages Package
"""
from .up_list_page import UPListPage
from .up_detail_page import UPDetailPage
from .up_form_page import UPFormPage
from .tup_list_page import TUPListPage
from .tup_detail_page import TUPDetailPage
from .tup_form_page import TUPFormPage
from .ls_list_page import LSListPage
from .ls_detail_page import LSDetailPage
from .ls_form_page import LSFormPage

__all__ = [
    'UPListPage', 'UPDetailPage', 'UPFormPage',
    'TUPListPage', 'TUPDetailPage', 'TUPFormPage',
    'LSListPage', 'LSDetailPage', 'LSFormPage',
]