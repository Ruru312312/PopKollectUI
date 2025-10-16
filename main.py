import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QSplitter, QPushButton,
    QScrollArea, QDialog, QGridLayout, QSizePolicy, QSpacerItem 
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap 

# --- Import the separated classes ---
from funko_pop import FunkoPop
from clickable_container import ClickableContainer
from add_item_dialog import AddItemDialog

class Home(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PopKollect")
        self.setGeometry(100, 100, 1200, 800)
        
        self.inventory = [] 
        self.grid_row = 0
        self.grid_col = 0
        self.max_cols = 4 
        self.initUI()

    def initUI(self):
        main_splitter = QSplitter(Qt.Horizontal)

        # --- Section 1: Logo and Add Button (Left - UPDATED for Tooltips) ---
        left_frame = QFrame(self)
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setStyleSheet("background-color: #333; color: white;")

        left_layout = QVBoxLayout(left_frame)
        logo_label = QLabel("POPKOLLECT", left_frame)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 24px; font-weight: bold; border: 2px solid grey; padding: 10px;")
        
        add_button = QPushButton("Add New Pop", left_frame)
        add_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        add_button.clicked.connect(self.open_add_item_dialog)

        # --- NEW BUTTONS SECTION ---
        
        sync_button = QPushButton("Sync", left_frame)
        sync_button.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; border-radius: 5px;") 
        # Tooltip for Sync
        sync_button.setToolTip("Syncronizes all values from the main database (ONE USE PER DAY)") 

        update_button = QPushButton("Update", left_frame)
        update_button.setStyleSheet("background-color: #FF9800; color: white; padding: 8px; border-radius: 5px;") 
        # Tooltip for Update
        update_button.setToolTip("Updates the market value live") 

        # Add buttons to the layout
        left_layout.addWidget(logo_label)
        left_layout.addSpacing(20)
        left_layout.addWidget(add_button)
        left_layout.addSpacing(15)
        left_layout.addWidget(sync_button)
        left_layout.addWidget(update_button)
        left_layout.addStretch(1)
        # --- END NEW BUTTONS SECTION ---

        main_splitter.addWidget(left_frame)

        # Section 2: Containers (Middle - No change)
        middle_frame = QFrame(self)
        middle_frame.setFrameShape(QFrame.StyledPanel)
        middle_frame.setStyleSheet("background-color: #222;")
        self.scroll_area = QScrollArea(middle_frame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.scroll_content_widget = QWidget()
        self.container_grid_layout = QGridLayout(self.scroll_content_widget) 
        self.container_grid_layout.setContentsMargins(10, 10, 10, 10)
        self.container_grid_layout.setSpacing(10)
        self.container_grid_layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed), 
            0, self.max_cols, 1, 1
        )
        self.container_grid_layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding), 
            999, 0, 1, self.max_cols
        )
        self.scroll_content_widget.setLayout(self.container_grid_layout)
        self.scroll_area.setWidget(self.scroll_content_widget)
        middle_layout = QVBoxLayout(middle_frame)
        middle_layout.addWidget(self.scroll_area)
        main_splitter.addWidget(middle_frame)

        # Section 3: Sidebar (Right - No change)
        right_frame = QFrame(self)
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setStyleSheet("background-color: #333; color: white;")
        right_layout = QVBoxLayout(right_frame)
        self.sidebar_label = QLabel("POP DETAILS (Click a Pop)", right_frame)
        self.sidebar_label.setAlignment(Qt.AlignCenter)
        self.sidebar_label.setStyleSheet("font-size: 18px; font-weight: bold; color: yellow;")
        right_layout.addWidget(self.sidebar_label)
        self.sidebar_image_label = QLabel("Click a Pop to see the Image", right_frame)
        self.sidebar_image_label.setAlignment(Qt.AlignCenter)
        self.sidebar_image_label.setFixedSize(200, 200) 
        self.sidebar_image_label.setStyleSheet("border: 1px solid #555;")
        right_layout.addWidget(self.sidebar_image_label)
        self.details_label = QLabel("Name:\nSeries:\nValue:", right_frame)
        self.details_label.setTextFormat(Qt.RichText)
        right_layout.addWidget(self.details_label)
        right_layout.addStretch(1)
        main_splitter.addWidget(right_frame)

        main_splitter.setSizes([100, 800, 300])
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

    # ... (Rest of the methods remain the same)
    def open_add_item_dialog(self):
        dialog = AddItemDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_pop = dialog.new_pop
            if new_pop:
                self.add_pop_to_ui(new_pop)
                self.inventory.append(new_pop)

    def add_pop_to_ui(self, pop_object: FunkoPop):
        container = ClickableContainer(pop_object, self.scroll_content_widget) 
        container.clicked.connect(self.display_pop_details) 
        
        self.container_grid_layout.addWidget(
            container, self.grid_row, self.grid_col
        )
        
        self.grid_col += 1
        if self.grid_col >= self.max_cols:
            self.grid_col = 0
            self.grid_row += 1
        
    def display_pop_details(self, pop_object: FunkoPop):
        self.sidebar_label.setText(f"Details for: {pop_object.name}")
        info = pop_object.get_info()
        
        details_text = (
            f"Name: <b>{info['name']}</b><br>"
            f"Series: {info['series']}<br>"
            f"Item No: {info['item_no']}<br>"
            f"Release Year: {info['release_year']}<br>"
            f"Barcode: {info['barcode']}<br>"
            f"Market Value: <b>${info['market_value']}</b>"
        )
        self.details_label.setText(details_text)

        if pop_object.image_path:
            pixmap = QPixmap(pop_object.image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.sidebar_image_label.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.sidebar_image_label.setPixmap(scaled_pixmap)
            else:
                self.sidebar_image_label.setText("🚫 Image failed to load.")
                self.sidebar_image_label.setStyleSheet("color: red; border: 1px solid #555;")
        else:
            self.sidebar_image_label.clear()
            self.sidebar_image_label.setText("No Image Available")
            self.sidebar_image_label.setStyleSheet("color: white; border: 1px solid #555;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Home()
    main_window.show()
    sys.exit(app.exec_())