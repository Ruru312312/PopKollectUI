# flow_layout.py (FINAL WORKING VERSION)

from PyQt5.QtWidgets import QLayout, QWidgetItem
from PyQt5.QtCore import QPoint, QRect, QSize, Qt

class FlowLayout(QLayout):
    """
    A custom QLayout that arranges widgets in a line and wraps them when 
    space is exhausted. It ensures the container widget expands vertically.
    """
    def __init__(self, parent=None, margin=-1, spacing=-1):
        super().__init__(parent)
        
        self.itemList = []
        self.m_spacing = spacing if spacing != -1 else 10 
        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addWidget(self, widget):
        self.addItem(QWidgetItem(widget))

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Vertical)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._doLayout(QRect(0, 0, width, 0), True)

    # --- CRITICAL FIX: Enforce minimum height on parent widget ---
    def setGeometry(self, rect):
        super().setGeometry(rect)
        required_height = self._doLayout(rect, False)
        
        if self.parentWidget():
            # This is the line that forces the scroll area content widget 
            # to resize vertically, making the items visible.
            self.parentWidget().setMinimumHeight(required_height)
    # -------------------------------------------------------------

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        width = self.geometry().width()
        if width <= 0:
            width = 400 

        height = self._doLayout(QRect(0, 0, width, 0), True)
        
        left, top, right, bottom = self.getContentsMargins()
        
        return QSize(width + left + right, height + top + bottom)

    def _doLayout(self, rect, testOnly):
        left, top, right, bottom = self.getContentsMargins()
        x = rect.x() + left
        y = rect.y() + top
        
        lineHeight = 0
        spaceX = self.m_spacing
        spaceY = self.m_spacing
        
        currentX = x
        currentY = y
        
        totalHeight = 0 
        
        for item in self.itemList:
            itemSize = item.sizeHint()
            
            # Check if the widget can fit on the current line
            if currentX + itemSize.width() > rect.right() - right and lineHeight > 0:
                # Move to the next row
                
                if totalHeight > 0:
                    totalHeight += spaceY
                totalHeight += lineHeight
                
                currentX = x 
                currentY = currentY + lineHeight + spaceY
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(currentX, currentY), itemSize))

            currentX += itemSize.width() + spaceX
            lineHeight = max(lineHeight, itemSize.height())

        # Final Height Calculation (for the last line)
        if lineHeight > 0:
            if totalHeight > 0:
                 totalHeight += spaceY
            totalHeight += lineHeight

        return totalHeight + bottom