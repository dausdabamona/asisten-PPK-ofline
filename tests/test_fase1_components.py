"""
PPK DOCUMENT FACTORY - Test Fase 1 Components
==============================================
Verifikasi semua komponen Fase 1 bekerja dengan baik.

Run:
    python -m pytest tests/test_fase1_components.py -v
    atau
    python tests/test_fase1_components.py
"""

import sys
import os
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Qt application before importing widgets
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Create QApplication instance (required for Qt widgets)
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestImports(unittest.TestCase):
    """Test 1: Pastikan semua module bisa di-import tanpa error."""

    def test_import_base_manager(self):
        """Test import base_manager module."""
        from app.ui.base import base_manager
        self.assertTrue(hasattr(base_manager, 'BaseManagerWidget'))

    def test_import_base_page(self):
        """Test import base_page module."""
        from app.ui.base import base_page
        self.assertTrue(hasattr(base_page, 'BasePage'))

    def test_import_base_form(self):
        """Test import base_form module."""
        from app.ui.base import base_form
        self.assertTrue(hasattr(base_form, 'BaseFormWidget'))
        self.assertTrue(hasattr(base_form, 'FormField'))
        self.assertTrue(hasattr(base_form, 'FormBuilder'))
        self.assertTrue(hasattr(base_form, 'FieldType'))

    def test_import_base_table(self):
        """Test import base_table module."""
        from app.ui.base import base_table
        self.assertTrue(hasattr(base_table, 'BaseTableWidget'))
        self.assertTrue(hasattr(base_table, 'ColumnDef'))
        self.assertTrue(hasattr(base_table, 'ActionDef'))

    def test_import_icon_provider(self):
        """Test import icon_provider module."""
        from app.ui.icons import icon_provider
        self.assertTrue(hasattr(icon_provider, 'IconProvider'))

    def test_import_dashboard_components(self):
        """Test import dashboard components."""
        from app.ui.dashboard_components import (
            StatisticsSection,
            MekanismeStatCard,
            SaldoUPWidget,
            QuickActionsWidget,
            QuickActionButton,
            RecentActivityWidget,
            TransactionItemWidget,
        )
        self.assertIsNotNone(StatisticsSection)
        self.assertIsNotNone(SaldoUPWidget)
        self.assertIsNotNone(QuickActionsWidget)
        self.assertIsNotNone(RecentActivityWidget)

    def test_import_base_init(self):
        """Test import from base __init__.py."""
        from app.ui.base import (
            BaseManagerWidget,
            BasePage,
            BaseFormWidget,
            FormField,
            FormBuilder,
            FieldType,
            BaseTableWidget,
            ColumnDef,
            ActionDef,
            # Validators
            required_validator,
            email_validator,
            nip_validator,
            # Formatters
            format_rupiah,
            format_date_id,
        )
        self.assertIsNotNone(BaseManagerWidget)
        self.assertIsNotNone(BasePage)
        self.assertIsNotNone(BaseFormWidget)
        self.assertIsNotNone(BaseTableWidget)


class TestInstantiation(unittest.TestCase):
    """Test 2: Buat instance setiap komponen."""

    def test_create_base_form_widget(self):
        """Test create BaseFormWidget instance."""
        from app.ui.base import BaseFormWidget
        widget = BaseFormWidget()
        self.assertIsNotNone(widget)
        widget.deleteLater()

    def test_create_base_table_widget(self):
        """Test create BaseTableWidget instance."""
        from app.ui.base import BaseTableWidget
        widget = BaseTableWidget()
        self.assertIsNotNone(widget)
        widget.deleteLater()

    def test_create_icon_provider(self):
        """Test create IconProvider instance."""
        from app.ui.icons import IconProvider
        provider = IconProvider()
        self.assertIsNotNone(provider)

    def test_create_statistics_section(self):
        """Test create StatisticsSection instance."""
        from app.ui.dashboard_components import StatisticsSection
        widget = StatisticsSection()
        self.assertIsNotNone(widget)
        widget.deleteLater()

    def test_create_saldo_up_widget(self):
        """Test create SaldoUPWidget instance."""
        from app.ui.dashboard_components import SaldoUPWidget
        widget = SaldoUPWidget()
        self.assertIsNotNone(widget)
        widget.deleteLater()

    def test_create_quick_actions_widget(self):
        """Test create QuickActionsWidget instance."""
        from app.ui.dashboard_components import QuickActionsWidget
        widget = QuickActionsWidget()
        self.assertIsNotNone(widget)
        widget.deleteLater()

    def test_create_recent_activity_widget(self):
        """Test create RecentActivityWidget instance."""
        from app.ui.dashboard_components import RecentActivityWidget
        widget = RecentActivityWidget()
        self.assertIsNotNone(widget)
        widget.deleteLater()

    def test_create_form_builder(self):
        """Test create form using FormBuilder."""
        from app.ui.base import FormBuilder
        form = (FormBuilder()
            .add_text('nama', 'Nama')
            .add_number('umur', 'Umur')
            .build())
        self.assertIsNotNone(form)
        form.deleteLater()


class TestBasicFunctionality(unittest.TestCase):
    """Test 3: Test basic functionality."""

    def test_icon_provider_get_icon(self):
        """Test IconProvider.get_icon() returns QIcon."""
        from app.ui.icons import IconProvider
        from PySide6.QtGui import QIcon

        provider = IconProvider()
        icon = provider.get_icon('dashboard')
        self.assertIsInstance(icon, QIcon)

    def test_icon_provider_get_pixmap(self):
        """Test IconProvider.get_pixmap() returns QPixmap."""
        from app.ui.icons import IconProvider
        from PySide6.QtGui import QPixmap

        pixmap = IconProvider.get_pixmap('dashboard')
        self.assertIsInstance(pixmap, QPixmap)

    def test_base_table_set_columns(self):
        """Test BaseTableWidget.set_columns() works."""
        from app.ui.base import BaseTableWidget, ColumnDef

        table = BaseTableWidget()
        columns = [
            ColumnDef('id', 'ID', width=50),
            ColumnDef('nama', 'Nama', stretch=True),
            ColumnDef('nilai', 'Nilai'),
        ]
        table.set_columns(columns)

        # Verify columns are set
        self.assertEqual(len(table._columns), 3)
        table.deleteLater()

    def test_base_table_set_data(self):
        """Test BaseTableWidget.set_data() works."""
        from app.ui.base import BaseTableWidget, ColumnDef

        table = BaseTableWidget()
        table.set_columns([
            ColumnDef('id', 'ID'),
            ColumnDef('nama', 'Nama'),
        ])

        data = [
            {'id': 1, 'nama': 'Item 1'},
            {'id': 2, 'nama': 'Item 2'},
            {'id': 3, 'nama': 'Item 3'},
        ]
        table.set_data(data)

        self.assertEqual(table.row_count, 3)
        self.assertEqual(table.total_count, 3)
        table.deleteLater()

    def test_base_table_filter_data(self):
        """Test BaseTableWidget.filter_data() works."""
        from app.ui.base import BaseTableWidget, ColumnDef

        table = BaseTableWidget()
        table.set_columns([
            ColumnDef('id', 'ID'),
            ColumnDef('status', 'Status'),
        ])

        data = [
            {'id': 1, 'status': 'active'},
            {'id': 2, 'status': 'inactive'},
            {'id': 3, 'status': 'active'},
        ]
        table.set_data(data)

        # Filter active only
        table.filter_data(lambda row: row['status'] == 'active')
        self.assertEqual(table.row_count, 2)
        self.assertEqual(table.total_count, 3)

        # Clear filter
        table.clear_filter()
        self.assertEqual(table.row_count, 3)
        table.deleteLater()

    def test_base_form_add_field(self):
        """Test BaseFormWidget.add_field() works."""
        from app.ui.base import BaseFormWidget, FieldType

        form = BaseFormWidget()
        form.add_field('nama', 'Nama Lengkap', required=True)
        form.add_field('email', 'Email', field_type=FieldType.TEXT)
        form.add_field('umur', 'Umur', field_type=FieldType.NUMBER, min_value=0)

        self.assertEqual(len(form.field_names), 3)
        self.assertIn('nama', form.field_names)
        self.assertIn('email', form.field_names)
        self.assertIn('umur', form.field_names)
        form.deleteLater()

    def test_base_form_get_set_values(self):
        """Test BaseFormWidget.get_values() and set_values() work."""
        from app.ui.base import BaseFormWidget

        form = BaseFormWidget()
        form.add_field('nama', 'Nama')
        form.add_field('kota', 'Kota')

        # Set values
        form.set_values({'nama': 'John Doe', 'kota': 'Jakarta'})

        # Get values
        values = form.get_values()
        self.assertEqual(values['nama'], 'John Doe')
        self.assertEqual(values['kota'], 'Jakarta')
        form.deleteLater()

    def test_base_form_validation(self):
        """Test BaseFormWidget validation works."""
        from app.ui.base import BaseFormWidget, required_validator

        form = BaseFormWidget()
        form.add_field('nama', 'Nama', required=True)
        form.add_field('opsional', 'Opsional')

        # Empty required field should fail
        form.set_values({'nama': '', 'opsional': ''})
        self.assertFalse(form.validate())

        # Filled required field should pass
        form.set_values({'nama': 'Test', 'opsional': ''})
        self.assertTrue(form.validate())
        form.deleteLater()

    def test_base_form_validators(self):
        """Test various validators work."""
        from app.ui.base import (
            email_validator,
            phone_validator,
            nip_validator,
            nik_validator,
            min_length_validator,
        )

        # Email validator
        self.assertTrue(email_validator('test@example.com').is_valid)
        self.assertFalse(email_validator('invalid-email').is_valid)

        # Phone validator
        self.assertTrue(phone_validator('08123456789').is_valid)
        self.assertTrue(phone_validator('+6281234567890').is_valid)

        # NIP validator (18 digits)
        self.assertTrue(nip_validator('199001012020121001').is_valid)
        self.assertFalse(nip_validator('12345').is_valid)

        # NIK validator (16 digits)
        self.assertTrue(nik_validator('3201012345678901').is_valid)
        self.assertFalse(nik_validator('12345').is_valid)

        # Min length validator
        min_3 = min_length_validator(3)
        self.assertTrue(min_3('abc').is_valid)
        self.assertFalse(min_3('ab').is_valid)

    def test_table_formatters(self):
        """Test table formatters work."""
        from app.ui.base import (
            format_rupiah,
            format_boolean,
            format_status_badge,
            truncate_text,
        )

        # format_rupiah
        self.assertEqual(format_rupiah(1000000), 'Rp 1.000.000')
        self.assertEqual(format_rupiah(None), 'Rp 0')

        # format_boolean
        self.assertEqual(format_boolean(True), 'Ya')
        self.assertEqual(format_boolean(False), 'Tidak')
        self.assertEqual(format_boolean(True, 'Aktif', 'Nonaktif'), 'Aktif')

        # format_status_badge
        formatter = format_status_badge({
            'active': '✅ Aktif',
            'inactive': '❌ Nonaktif'
        })
        self.assertEqual(formatter('active'), '✅ Aktif')
        self.assertEqual(formatter('inactive'), '❌ Nonaktif')

        # truncate_text
        truncate = truncate_text(10)
        self.assertEqual(truncate('short'), 'short')
        self.assertEqual(truncate('this is a very long text'), 'this is...')

    def test_dashboard_statistics_update(self):
        """Test StatisticsSection.update_statistics() works."""
        from app.ui.dashboard_components import StatisticsSection

        widget = StatisticsSection()

        # Update with data using correct API
        stats = {
            'UP': {'total': 10, 'nilai': 50000000, 'selesai': 5},
            'TUP': {'total': 5, 'nilai': 25000000, 'selesai': 3},
            'LS': {'total': 3, 'nilai': 15000000, 'selesai': 2},
        }
        widget.update_statistics(stats)

        # Widget should not crash
        self.assertIsNotNone(widget)
        widget.deleteLater()

    def test_dashboard_saldo_update(self):
        """Test SaldoUPWidget.update_saldo() works."""
        from app.ui.dashboard_components import SaldoUPWidget

        widget = SaldoUPWidget()

        # Update saldo using correct API: tersedia, terpakai
        widget.update_saldo(
            tersedia=40000000,
            terpakai=10000000
        )

        self.assertIsNotNone(widget)
        widget.deleteLater()

    def test_dashboard_recent_activity(self):
        """Test RecentActivityWidget.set_transactions() works."""
        from app.ui.dashboard_components import RecentActivityWidget

        widget = RecentActivityWidget()

        # Set transactions
        transactions = [
            {
                'id': 'UP-001',
                'mekanisme': 'UP',
                'nama': 'Belanja ATK',
                'nilai': 5000000,
                'status': 'proses',
                'tanggal': '2024-01-15'
            },
            {
                'id': 'LS-001',
                'mekanisme': 'LS',
                'nama': 'Pengadaan Laptop',
                'nilai': 15000000,
                'status': 'selesai',
                'tanggal': '2024-01-14'
            }
        ]
        widget.set_transactions(transactions)

        self.assertEqual(len(widget.get_transactions()), 2)
        widget.deleteLater()


class TestFormBuilder(unittest.TestCase):
    """Test FormBuilder fluent API."""

    def test_form_builder_all_field_types(self):
        """Test FormBuilder with all field types."""
        from app.ui.base import FormBuilder

        form = (FormBuilder()
            .add_text('text_field', 'Text Field')
            .add_password('password_field', 'Password')
            .add_textarea('textarea_field', 'Textarea')
            .add_number('number_field', 'Number', min_value=0, max_value=100)
            .add_decimal('decimal_field', 'Decimal')
            .add_currency('currency_field', 'Currency')
            .add_date('date_field', 'Date')
            .add_time('time_field', 'Time')
            .add_combo('combo_field', 'Combo', options=[
                ('opt1', 'Option 1'),
                ('opt2', 'Option 2')
            ])
            .add_checkbox('checkbox_field', 'Checkbox')
            .build())

        self.assertEqual(len(form.field_names), 10)
        form.deleteLater()


class TestToastNotifications(unittest.TestCase):
    """Test Toast notification system."""

    def test_import_toast_components(self):
        """Test import toast components."""
        from app.ui.components.toast import (
            Toast,
            ToastType,
            ToastContainer,
            ToastManager,
        )
        self.assertIsNotNone(Toast)
        self.assertIsNotNone(ToastType)
        self.assertIsNotNone(ToastContainer)
        self.assertIsNotNone(ToastManager)

    def test_toast_types(self):
        """Test ToastType enum values."""
        from app.ui.components.toast import ToastType

        self.assertEqual(ToastType.SUCCESS.value, "success")
        self.assertEqual(ToastType.ERROR.value, "error")
        self.assertEqual(ToastType.WARNING.value, "warning")
        self.assertEqual(ToastType.INFO.value, "info")

    def test_create_toast(self):
        """Test creating Toast widget."""
        from app.ui.components.toast import Toast, ToastType

        toast = Toast("Test message", ToastType.SUCCESS)
        self.assertIsNotNone(toast)
        self.assertEqual(toast.message, "Test message")
        self.assertEqual(toast.toast_type, ToastType.SUCCESS)
        toast.deleteLater()

    def test_create_toast_all_types(self):
        """Test creating Toast for all types."""
        from app.ui.components.toast import Toast, ToastType

        for toast_type in ToastType:
            toast = Toast(f"Test {toast_type.value}", toast_type)
            self.assertIsNotNone(toast)
            self.assertEqual(toast.toast_type, toast_type)
            toast.deleteLater()

    def test_toast_container_creation(self):
        """Test creating ToastContainer."""
        from app.ui.components.toast import ToastContainer

        container = ToastContainer()
        self.assertIsNotNone(container)
        container.deleteLater()

    def test_convenience_functions(self):
        """Test convenience functions exist."""
        from app.ui.components.toast import (
            show_toast,
            toast_success,
            toast_error,
            toast_warning,
            toast_info,
        )
        self.assertTrue(callable(show_toast))
        self.assertTrue(callable(toast_success))
        self.assertTrue(callable(toast_error))
        self.assertTrue(callable(toast_warning))
        self.assertTrue(callable(toast_info))

    def test_toast_from_components_init(self):
        """Test toast imports from components __init__."""
        from app.ui.components import (
            Toast,
            ToastType,
            ToastManager,
            toast_success,
            toast_error,
        )
        self.assertIsNotNone(Toast)
        self.assertIsNotNone(ToastType)
        self.assertIsNotNone(ToastManager)


class TestNewComponents(unittest.TestCase):
    """Test new UI components (confirm_dialog, search_bar, breadcrumb, status_badge)."""

    def test_import_confirm_dialog(self):
        """Test import ConfirmDialog components."""
        from app.ui.components import (
            ConfirmDialog,
            DialogType,
            InputDialog,
            InputType,
        )
        self.assertIsNotNone(ConfirmDialog)
        self.assertIsNotNone(DialogType)
        self.assertIsNotNone(InputDialog)
        self.assertIsNotNone(InputType)

    def test_dialog_types(self):
        """Test DialogType enum values."""
        from app.ui.components import DialogType

        self.assertEqual(DialogType.CONFIRM.value, "confirm")
        self.assertEqual(DialogType.WARNING.value, "warning")
        self.assertEqual(DialogType.DANGER.value, "danger")
        self.assertEqual(DialogType.INFO.value, "info")

    def test_create_confirm_dialog(self):
        """Test creating ConfirmDialog."""
        from app.ui.components import ConfirmDialog, DialogType

        dialog = ConfirmDialog(
            title="Test",
            message="Test message",
            dialog_type=DialogType.CONFIRM
        )
        self.assertIsNotNone(dialog)
        dialog.deleteLater()

    def test_create_input_dialog(self):
        """Test creating InputDialog."""
        from app.ui.components import InputDialog, InputType

        dialog = InputDialog(
            title="Input",
            label="Enter value:",
            input_type=InputType.TEXT
        )
        self.assertIsNotNone(dialog)
        dialog.deleteLater()

    def test_import_search_bar(self):
        """Test import SearchBar components."""
        from app.ui.components import (
            SearchBar,
            AdvancedSearchBar,
            create_search_bar,
        )
        self.assertIsNotNone(SearchBar)
        self.assertIsNotNone(AdvancedSearchBar)
        self.assertTrue(callable(create_search_bar))

    def test_create_search_bar(self):
        """Test creating SearchBar."""
        from app.ui.components import SearchBar

        search = SearchBar(placeholder="Search...", debounce_ms=300)
        self.assertIsNotNone(search)

        # Test text operations
        search.set_text("test")
        self.assertEqual(search.get_text(), "test")

        search.clear()
        self.assertEqual(search.get_text(), "")

        search.deleteLater()

    def test_search_bar_filters(self):
        """Test SearchBar filters."""
        from app.ui.components import SearchBar

        search = SearchBar()
        search.add_filter("status", ["Semua", "Aktif", "Selesai"])
        search.add_filter("type", ["All", "Type A", "Type B"])

        filters = search.get_all_filter_values()
        self.assertEqual(len(filters), 2)
        self.assertEqual(filters["status"], "Semua")
        self.assertEqual(filters["type"], "All")

        search.deleteLater()

    def test_import_breadcrumb(self):
        """Test import Breadcrumb components."""
        from app.ui.components import (
            Breadcrumb,
            BreadcrumbItem,
            create_breadcrumb,
        )
        self.assertIsNotNone(Breadcrumb)
        self.assertIsNotNone(BreadcrumbItem)
        self.assertTrue(callable(create_breadcrumb))

    def test_create_breadcrumb(self):
        """Test creating Breadcrumb."""
        from app.ui.components import Breadcrumb, BreadcrumbItem

        bc = Breadcrumb()
        bc.set_items([
            BreadcrumbItem("Dashboard", "dashboard"),
            BreadcrumbItem("UP", "up"),
            BreadcrumbItem("Detail", "detail"),
        ])

        items = bc.get_items()
        self.assertEqual(len(items), 3)

        current = bc.get_current()
        self.assertEqual(current.label, "Detail")
        self.assertEqual(current.path, "detail")

        bc.deleteLater()

    def test_breadcrumb_push_pop(self):
        """Test Breadcrumb push and pop."""
        from app.ui.components import Breadcrumb

        bc = Breadcrumb()
        bc.push("Home", "home")
        bc.push("Page 1", "page1")
        bc.push("Page 2", "page2")

        self.assertEqual(len(bc.get_items()), 3)

        popped = bc.pop()
        self.assertEqual(popped.label, "Page 2")
        self.assertEqual(len(bc.get_items()), 2)

        bc.deleteLater()

    def test_import_status_badge(self):
        """Test import StatusBadge components."""
        from app.ui.components import (
            StatusBadge,
            StatusType,
            MekanismeBadge,
            FaseBadge,
            FaseStatus,
            PriorityBadge,
        )
        self.assertIsNotNone(StatusBadge)
        self.assertIsNotNone(StatusType)
        self.assertIsNotNone(MekanismeBadge)
        self.assertIsNotNone(FaseBadge)
        self.assertIsNotNone(FaseStatus)
        self.assertIsNotNone(PriorityBadge)

    def test_create_status_badge(self):
        """Test creating StatusBadge."""
        from app.ui.components import StatusBadge

        badge = StatusBadge("Selesai", "completed", size="medium")
        self.assertIsNotNone(badge)
        badge.deleteLater()

    def test_status_badge_custom_color(self):
        """Test StatusBadge custom colors."""
        from app.ui.components import StatusBadge

        badge = StatusBadge("Custom", "default")
        badge.set_custom_color("#9b59b6", "#ffffff")
        self.assertIsNotNone(badge)
        badge.deleteLater()

    def test_create_mekanisme_badge(self):
        """Test creating MekanismeBadge."""
        from app.ui.components import MekanismeBadge

        for mek in ["UP", "TUP", "LS"]:
            badge = MekanismeBadge(mek)
            self.assertIsNotNone(badge)
            badge.deleteLater()

    def test_create_fase_badge(self):
        """Test creating FaseBadge."""
        from app.ui.components import FaseBadge, FaseStatus

        for status in FaseStatus:
            badge = FaseBadge(1, "Test Fase", status)
            self.assertIsNotNone(badge)
            badge.deleteLater()

    def test_create_priority_badge(self):
        """Test creating PriorityBadge."""
        from app.ui.components import PriorityBadge

        for priority in ["low", "medium", "high", "urgent"]:
            badge = PriorityBadge(priority)
            self.assertIsNotNone(badge)
            badge.deleteLater()


class TestShortcutManager(unittest.TestCase):
    """Test ShortcutManager system."""

    def test_import_shortcuts(self):
        """Test import shortcuts components."""
        from app.ui.shortcuts import (
            ShortcutManager,
            ShortcutInfo,
            ShortcutContext,
            ShortcutHelpDialog,
            get_shortcut_manager,
        )
        self.assertIsNotNone(ShortcutManager)
        self.assertIsNotNone(ShortcutInfo)
        self.assertIsNotNone(ShortcutContext)
        self.assertIsNotNone(ShortcutHelpDialog)
        self.assertTrue(callable(get_shortcut_manager))

    def test_shortcut_manager_singleton(self):
        """Test ShortcutManager singleton pattern."""
        from app.ui.shortcuts import ShortcutManager

        manager1 = ShortcutManager()
        manager2 = ShortcutManager()
        self.assertIs(manager1, manager2)

    def test_shortcut_info_dataclass(self):
        """Test ShortcutInfo dataclass."""
        from app.ui.shortcuts import ShortcutInfo

        info = ShortcutInfo(
            key_sequence="Ctrl+N",
            description="New item",
            context="global",
            enabled=True
        )
        self.assertEqual(info.key_sequence, "Ctrl+N")
        self.assertEqual(info.description, "New item")
        self.assertEqual(info.context, "global")
        self.assertTrue(info.enabled)

    def test_shortcut_context_enum(self):
        """Test ShortcutContext enum."""
        from app.ui.shortcuts import ShortcutContext

        self.assertEqual(ShortcutContext.GLOBAL.value, "global")
        self.assertEqual(ShortcutContext.NAVIGATION.value, "navigation")
        self.assertEqual(ShortcutContext.FORM.value, "form")


class TestIntegrations(unittest.TestCase):
    """Test component integrations."""

    def test_utils_import(self):
        """Test utils module imports."""
        from app.ui.utils import (
            show_toast,
            show_success,
            show_error,
            show_warning,
            show_info,
            confirm,
            confirm_warning,
            confirm_danger,
            get_text_input,
            format_rupiah,
            format_tanggal,
            truncate_text,
        )
        self.assertTrue(callable(show_toast))
        self.assertTrue(callable(show_success))
        self.assertTrue(callable(confirm))

    def test_utils_format_rupiah(self):
        """Test format_rupiah utility."""
        from app.ui.utils import format_rupiah

        self.assertEqual(format_rupiah(1000000), "Rp 1.000.000")
        self.assertEqual(format_rupiah(0), "Rp 0")
        self.assertEqual(format_rupiah(None), "Rp 0")

    def test_utils_truncate_text(self):
        """Test truncate_text utility."""
        from app.ui.utils import truncate_text

        self.assertEqual(truncate_text("short", 10), "short")
        self.assertEqual(truncate_text("this is a very long text", 10), "this is...")
        self.assertEqual(truncate_text("", 10), "")

    def test_base_manager_has_toast_methods(self):
        """Test BaseManagerWidget has toast integration."""
        from app.ui.base import BaseManagerWidget

        # Check methods exist
        self.assertTrue(hasattr(BaseManagerWidget, 'show_error'))
        self.assertTrue(hasattr(BaseManagerWidget, 'show_success'))
        self.assertTrue(hasattr(BaseManagerWidget, 'show_warning'))
        self.assertTrue(hasattr(BaseManagerWidget, 'show_info'))
        self.assertTrue(hasattr(BaseManagerWidget, 'confirm'))
        self.assertTrue(hasattr(BaseManagerWidget, 'confirm_danger'))

    def test_base_page_has_toast_methods(self):
        """Test BasePage has toast integration."""
        from app.ui.base import BasePage

        # Check methods exist
        self.assertTrue(hasattr(BasePage, 'show_error'))
        self.assertTrue(hasattr(BasePage, 'show_success'))
        self.assertTrue(hasattr(BasePage, 'show_warning'))
        self.assertTrue(hasattr(BasePage, 'show_info'))
        self.assertTrue(hasattr(BasePage, 'confirm'))
        self.assertTrue(hasattr(BasePage, 'confirm_danger'))

    def test_base_table_empty_state_methods(self):
        """Test BaseTableWidget empty state methods."""
        from app.ui.base import BaseTableWidget

        table = BaseTableWidget()

        # Check methods exist
        self.assertTrue(hasattr(table, 'set_empty_state'))
        self.assertTrue(hasattr(table, 'set_search_empty_state'))

        # Test set_empty_state
        table.set_empty_state(
            title="No data",
            description="Add some data",
            icon="[icon]",
            action_text="Add New"
        )

        table.deleteLater()

    def test_ui_utils_from_ui_init(self):
        """Test utils can be imported from app.ui."""
        from app.ui import (
            show_toast,
            show_success,
            show_error,
            confirm,
            format_rupiah,
            truncate_text,
        )
        self.assertTrue(callable(show_toast))
        self.assertTrue(callable(confirm))
        self.assertTrue(callable(format_rupiah))


class TestActionColumn(unittest.TestCase):
    """Test BaseTableWidget action column."""

    def test_action_column_creation(self):
        """Test adding action column to table."""
        from app.ui.base import BaseTableWidget, ColumnDef, ActionDef

        table = BaseTableWidget()
        table.set_columns([
            ColumnDef('id', 'ID'),
            ColumnDef('nama', 'Nama'),
        ])

        actions = [
            ActionDef('edit', 'Edit', icon='[E]'),
            ActionDef('delete', 'Hapus', icon='[D]', color='#e74c3c'),
        ]
        table.add_action_column(actions)

        # Set data to trigger rendering
        table.set_data([{'id': 1, 'nama': 'Test'}])

        self.assertEqual(len(table._actions), 2)
        table.deleteLater()

    def test_action_callback(self):
        """Test action callback is called."""
        from app.ui.base import BaseTableWidget, ColumnDef, ActionDef

        callback_called = {'value': False}

        def on_edit(row_idx, row_data):
            callback_called['value'] = True

        table = BaseTableWidget()
        table.set_columns([ColumnDef('id', 'ID')])
        table.add_action_column([
            ActionDef('edit', 'Edit', callback=on_edit)
        ])
        table.set_data([{'id': 1}])

        # Simulate action click
        table._on_action_clicked('edit', 0)

        self.assertTrue(callback_called['value'])
        table.deleteLater()


def run_tests():
    """Run all tests and print summary."""
    print("=" * 70)
    print("PPK DOCUMENT FACTORY - Fase 1 Component Tests")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestImports))
    suite.addTests(loader.loadTestsFromTestCase(TestInstantiation))
    suite.addTests(loader.loadTestsFromTestCase(TestBasicFunctionality))
    suite.addTests(loader.loadTestsFromTestCase(TestFormBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestToastNotifications))
    suite.addTests(loader.loadTestsFromTestCase(TestNewComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestShortcutManager))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrations))
    suite.addTests(loader.loadTestsFromTestCase(TestActionColumn))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print()
        print("[PASS] ALL TESTS PASSED!")
    else:
        print()
        print("[FAIL] SOME TESTS FAILED!")

        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}")

        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}")

    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
