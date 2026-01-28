"""
Workflow Main Window - Main window dengan sidebar dan QStackedWidget untuk workflow pencairan dana
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QStackedWidget, QLabel, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.ui.sidebar import SidebarNavigation
from app.ui.pages.pencairan.up_list_page import UPListPage
from app.ui.pages.pencairan.up_detail_page import UPDetailPage
from app.ui.pages.pencairan.up_form_page import UPFormPage
from app.ui.pages.pencairan.tup_list_page import TUPListPage
from app.ui.pages.pencairan.tup_detail_page import TUPDetailPage
from app.ui.pages.pencairan.tup_form_page import TUPFormPage
from app.ui.pages.pencairan.ls_list_page import LSListPage
from app.ui.pages.pencairan.ls_detail_page import LSDetailPage
from app.ui.pages.pencairan.ls_form_page import LSFormPage


class WorkflowMainWindow(QMainWindow):
    """Main window dengan sidebar dan workflow pages"""
    
    # Page indices untuk QStackedWidget
    PAGE_DASHBOARD = 0
    PAGE_UP_LIST = 1
    PAGE_UP_DETAIL = 2
    PAGE_UP_FORM = 3
    PAGE_TUP_LIST = 4
    PAGE_TUP_DETAIL = 5
    PAGE_TUP_FORM = 6
    PAGE_LS_LIST = 7
    PAGE_LS_DETAIL = 8
    PAGE_LS_FORM = 9
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PPK Document Factory - Workflow Pencairan Dana')
        self.setGeometry(100, 100, 1400, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = SidebarNavigation()
        self.sidebar.menu_clicked.connect(self.on_menu_clicked)
        main_layout.addWidget(self.sidebar)
        
        # Create stacked widget untuk pages
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create pages
        self._create_pages()
        
        # Connect signals
        self._connect_signals()
        
        # Set main widget
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Set initial page
        self.sidebar.set_active_menu('up')
        self.show_page('up')
    
    def _create_pages(self):
        """Create all pages"""
        # Dashboard (placeholder)
        dashboard = self._create_dashboard_page()
        self.stacked_widget.addWidget(dashboard)
        
        # UP Pages
        self.up_list_page = UPListPage()
        self.stacked_widget.addWidget(self.up_list_page)
        
        self.up_detail_page = UPDetailPage()
        self.stacked_widget.addWidget(self.up_detail_page)
        
        self.up_form_page = UPFormPage()
        self.stacked_widget.addWidget(self.up_form_page)
        
        # TUP Pages
        self.tup_list_page = TUPListPage()
        self.stacked_widget.addWidget(self.tup_list_page)
        
        self.tup_detail_page = TUPDetailPage()
        self.stacked_widget.addWidget(self.tup_detail_page)
        
        self.tup_form_page = TUPFormPage()
        self.stacked_widget.addWidget(self.tup_form_page)
        
        # LS Pages
        self.ls_list_page = LSListPage()
        self.stacked_widget.addWidget(self.ls_list_page)
        
        self.ls_detail_page = LSDetailPage()
        self.stacked_widget.addWidget(self.ls_detail_page)
        
        self.ls_form_page = LSFormPage()
        self.stacked_widget.addWidget(self.ls_form_page)
    
    def _create_dashboard_page(self) -> QWidget:
        """Create dashboard page"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('📊 Dashboard Pencairan Dana')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Placeholder
        placeholder = QLabel('Dashboard coming soon...')
        layout.addStretch()
        layout.addWidget(placeholder)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _connect_signals(self):
        """Connect signals dari pages"""
        # UP Page signals
        self.up_list_page.transaksi_selected.connect(lambda tid: self.show_up_detail(tid))
        self.up_list_page.create_new_requested.connect(lambda: self.show_page('up_form'))
        self.up_detail_page.back_requested.connect(lambda: self.show_page('up'))
        self.up_detail_page.transaksi_updated.connect(lambda tid: self.show_up_detail(tid))
        self.up_form_page.back_requested.connect(lambda: self.show_page('up'))
        self.up_form_page.transaksi_created.connect(lambda tid: self.show_up_detail(tid))
        
        # TUP Page signals
        self.tup_list_page.transaksi_selected.connect(lambda tid: self.show_tup_detail(tid))
        self.tup_list_page.create_new_requested.connect(lambda: self.show_page('tup_form'))
        self.tup_detail_page.back_requested.connect(lambda: self.show_page('tup'))
        self.tup_detail_page.transaksi_updated.connect(lambda tid: self.show_tup_detail(tid))
        self.tup_form_page.back_requested.connect(lambda: self.show_page('tup'))
        self.tup_form_page.transaksi_created.connect(lambda tid: self.show_tup_detail(tid))
        
        # LS Page signals
        self.ls_list_page.transaksi_selected.connect(lambda tid: self.show_ls_detail(tid))
        self.ls_list_page.create_new_requested.connect(lambda: self.show_page('ls_form'))
        self.ls_detail_page.back_requested.connect(lambda: self.show_page('ls'))
        self.ls_detail_page.transaksi_updated.connect(lambda tid: self.show_ls_detail(tid))
        self.ls_form_page.back_requested.connect(lambda: self.show_page('ls'))
        self.ls_form_page.transaksi_created.connect(lambda tid: self.show_ls_detail(tid))
    
    def on_menu_clicked(self, menu_id: str):
        """Handle menu click dari sidebar"""
        self.show_page(menu_id)
    
    def show_page(self, page_id: str):
        """Show page by ID"""
        if page_id == 'dashboard':
            self.stacked_widget.setCurrentIndex(self.PAGE_DASHBOARD)
        elif page_id == 'up':
            self.up_list_page.load_data()
            self.stacked_widget.setCurrentIndex(self.PAGE_UP_LIST)
        elif page_id == 'up_form':
            self.up_form_page.reset_form()
            self.stacked_widget.setCurrentIndex(self.PAGE_UP_FORM)
        elif page_id == 'tup':
            self.tup_list_page.load_data()
            self.stacked_widget.setCurrentIndex(self.PAGE_TUP_LIST)
        elif page_id == 'tup_form':
            self.tup_form_page.reset_form()
            self.stacked_widget.setCurrentIndex(self.PAGE_TUP_FORM)
        elif page_id == 'ls':
            self.ls_list_page.load_data()
            self.stacked_widget.setCurrentIndex(self.PAGE_LS_LIST)
        elif page_id == 'ls_form':
            self.ls_form_page.reset_form()
            self.stacked_widget.setCurrentIndex(self.PAGE_LS_FORM)
    
    def show_up_detail(self, transaksi_id: int):
        """Show UP detail page"""
        self.up_detail_page.load_data(transaksi_id)
        self.stacked_widget.setCurrentIndex(self.PAGE_UP_DETAIL)
    
    def show_tup_detail(self, transaksi_id: int):
        """Show TUP detail page"""
        self.tup_detail_page.load_data(transaksi_id)
        self.stacked_widget.setCurrentIndex(self.PAGE_TUP_DETAIL)
    
    def show_ls_detail(self, transaksi_id: int):
        """Show LS detail page"""
        self.ls_detail_page.load_data(transaksi_id)
        self.stacked_widget.setCurrentIndex(self.PAGE_LS_DETAIL)
