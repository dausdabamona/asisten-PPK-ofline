"""
PPK DOCUMENT FACTORY - Flow Layout Component
=============================================
A responsive layout that wraps widgets to the next line when there's not enough space.
Similar to CSS flex-wrap: wrap.
"""

from PySide6.QtWidgets import QLayout, QWidget, QSizePolicy, QLayoutItem
from PySide6.QtCore import Qt, QRect, QSize, QPoint


class FlowLayout(QLayout):
    """
    A layout that arranges widgets horizontally and wraps to next line when needed.
    
    This is similar to CSS flexbox with flex-wrap: wrap behavior.
    Useful for button groups that need to be responsive.
    """
    
    def __init__(self, parent=None, margin: int = 0, h_spacing: int = 5, v_spacing: int = 5):
        super().__init__(parent)
        
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self._items = []
    
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        """Add a QLayoutItem to the layout."""
        self._items.append(item)
    
    def horizontalSpacing(self) -> int:
        """Return horizontal spacing."""
        if self._h_spacing >= 0:
            return self._h_spacing
        return self._smartSpacing(QSizePolicy.LayoutType.HorizontalSpacing)
    
    def verticalSpacing(self) -> int:
        """Return vertical spacing."""
        if self._v_spacing >= 0:
            return self._v_spacing
        return self._smartSpacing(QSizePolicy.LayoutType.VerticalSpacing)
    
    def setHorizontalSpacing(self, spacing: int):
        """Set horizontal spacing."""
        self._h_spacing = spacing
    
    def setVerticalSpacing(self, spacing: int):
        """Set vertical spacing."""
        self._v_spacing = spacing
    
    def count(self) -> int:
        """Return number of items in layout."""
        return len(self._items)
    
    def itemAt(self, index: int) -> QLayoutItem:
        """Return item at given index."""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
    
    def takeAt(self, index: int) -> QLayoutItem:
        """Remove and return item at given index."""
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None
    
    def expandingDirections(self) -> Qt.Orientations:
        """Return expanding directions."""
        return Qt.Orientation(0)
    
    def hasHeightForWidth(self) -> bool:
        """Height depends on width (wrapping behavior)."""
        return True
    
    def heightForWidth(self, width: int) -> int:
        """Calculate height for given width."""
        return self._doLayout(QRect(0, 0, width, 0), test_only=True)
    
    def setGeometry(self, rect: QRect):
        """Set the layout geometry."""
        super().setGeometry(rect)
        self._doLayout(rect, test_only=False)
    
    def sizeHint(self) -> QSize:
        """Return the preferred size."""
        return self.minimumSize()
    
    def minimumSize(self) -> QSize:
        """Return minimum size needed."""
        size = QSize()
        
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        
        return size
    
    def _doLayout(self, rect: QRect, test_only: bool = False) -> int:
        """
        Perform the actual layout calculation and optionally apply it.
        
        Args:
            rect: The available rectangle for layout
            test_only: If True, just calculate height without applying
            
        Returns:
            The calculated height
        """
        margins = self.contentsMargins()
        effective_rect = rect.adjusted(
            margins.left(), margins.top(),
            -margins.right(), -margins.bottom()
        )
        
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0
        
        h_space = self.horizontalSpacing()
        v_space = self.verticalSpacing()
        
        for item in self._items:
            widget = item.widget()
            if widget is None:
                continue
                
            # Skip hidden widgets
            if not widget.isVisible():
                continue
            
            space_x = h_space
            space_y = v_space
            
            item_size = item.sizeHint()
            next_x = x + item_size.width() + space_x
            
            # Check if we need to wrap to next line
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item_size.width() + space_x
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item_size))
            
            x = next_x
            line_height = max(line_height, item_size.height())
        
        return y + line_height - rect.y() + margins.bottom()
    
    def _smartSpacing(self, layout_type) -> int:
        """Get smart spacing based on parent."""
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(layout_type, None, parent)
        else:
            return parent.spacing()
