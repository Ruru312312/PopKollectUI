# clickable_container.py (UPDATED)

import sys
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal, QSize 
from PyQt5.QtGui import QPixmap # <-- Added QPixmap

from funko_pop import FunkoPop 

class ClickableContainer(QFrame):
    clicked = pyqtSignal(FunkoPop) 

    def __init__(self, pop_object: FunkoPop, parent=None):
        super().__init__(parent)
        self.pop_object = pop_object
        self.setFrameShape(QFrame.StyledPanel)
        
        self.fixed_pop_size = QSize(200, 120) 
        self.setFixedSize(self.fixed_pop_size) 
        # ... (Stylesheet remains the same)
        self.setStyleSheet("""
            ClickableContainer {
                background-color: #444; 
                border: 1px solid #666; 
                border-radius: 5px;
                padding: 5px;
            }
            ClickableContainer:hover {
                background-color: #555; 
            }
        """)
        self.initContainerUI()
        
    
    def sizeHint(self):
        return self.fixed_pop_size

    def initContainerUI(self):
        v_layout = QVBoxLayout(self)
        
        # --- Image Loading Logic ---
        image_label = QLabel(self)
        image_label.setAlignment(Qt.AlignCenter)
        
        if self.pop_object.image_path:
            # Load image from path
            pixmap = QPixmap(self.pop_object.image_path)
            
            if not pixmap.isNull():
                # Scale the pixmap to fit the label (e.g., 60x60)
                scaled_pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
            else:
                # Fallback if image path is bad or file corrupted
                image_label.setText("🚫 IMG LOAD FAILED")
                image_label.setStyleSheet("font-size: 10px; color: red;")
        else:
            # Placeholder for no image
            image_label.setText("👤")
            image_label.setStyleSheet("font-size: 30px; color: #BBB;")
            
        # ---------------------------

        name_label = QLabel(self.pop_object.name, self)
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        name_label.setAlignment(Qt.AlignCenter)
        # ... (rest of labels remain the same)
        series_label = QLabel(f"Series: {self.pop_object.series}", self)
        series_label.setStyleSheet("color: #AAA; font-size: 10px;")
        series_label.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(f"Value: ${self.pop_object.market_value:.2f}", self)
        value_label.setStyleSheet("color: #add8e6; font-size: 12px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignCenter)

        # Replace image_placeholder with the new image_label
        v_layout.addWidget(image_label)
        v_layout.addWidget(name_label)
        v_layout.addWidget(series_label)
        v_layout.addWidget(value_label)
        v_layout.addStretch(1)

        # #edit and delete buttons
        # core_buttons_layout = QHBoxLayout()
        # self.edit_btn = QPushButton("Edit")
        # self.delete_btn = QPushButton("Delete")

        # core_buttons_layout.addWidget(self.edit_btn)
        # core_buttons_layout.addWidget(self.delete_btn)

        # v_layout.addLayout(core_buttons_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.pop_object) 
        super().mousePressEvent(event)