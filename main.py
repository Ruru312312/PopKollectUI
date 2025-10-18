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
from pop_details_dialog import PopDetailsDialog
from funko_db import FunkoDB

FunkoDB.create_table()  # Ensure the database table exists

class Home(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PopKollect")
        self.setGeometry(100, 100, 1200, 800)
        
        self.current_pop = None
        self.inventory = []
        self.grid_row = 0
        self.grid_col = 0
        self.max_cols = 4
        self.initUI()
        self.refresh_ui()

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

        # edit and delete buttons
        core_buttons_frame = QFrame()
        core_layout = QHBoxLayout(core_buttons_frame)

        self.edit_button = QPushButton("Edit")
        self.edit_button.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; border-radius: 5px;")
        self.edit_button.setToolTip("Edit the selected Pop's details")
        self.edit_button.setEnabled(False)  # Initially disabled

        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet("background-color: #FF9800; color: white; padding: 8px; border-radius: 5px;")
        self.delete_button.setToolTip("Delete the selected Pop from your collection")
        self.delete_button.setEnabled(False)  # Initially disabled

        core_layout.addWidget(self.edit_button)
        core_layout.addWidget(self.delete_button)

        # add buttons to the right sidebar
        right_layout.addWidget(core_buttons_frame)
        right_layout.addStretch(1)

        main_splitter.addWidget(right_frame)

        main_splitter.setSizes([100, 800, 300])
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

        # BUTTON FUNCTIONS
        # Connect edit and delete buttons
        self.edit_button.clicked.connect(self.open_edit_pop_dialog)
        self.delete_button.clicked.connect(self.delete_funko)

    def open_edit_pop_dialog(self):
        if hasattr(self, "current_pop") and self.current_pop:
            dialog = PopDetailsDialog(self.current_pop, self)
            result = dialog.exec_()

            if result == QDialog.Accepted:
                print("Funko updated!")
                self.refresh_ui()
            elif result == 99:  # Custom code for deletion
                print("Funko deleted!")
                self.refresh_ui()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "No Pop Selected", "Please select a Funko to edit.")

    def open_add_item_dialog(self):
        dialog = AddItemDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_pop = dialog.new_pop
            if new_pop:
                self.refresh_ui()

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
        self.current_pop = pop_object
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.sidebar_label.setText(f"Details for: {pop_object.name}")
        info = pop_object.get_info()

        details_text = (
            f"Barcode: {info['barcode']}<br>"
            f"Name: <b>{info['name']}</b><br>"
            f"Series: {info['series']}<br>"
            f"Item Number: {info['item_number']}<br>"
            f"Release Year: {info['year']}<br>"
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
                self.sidebar_image_label.setStyleSheet("border: 1px solid #555; color: white;")
            else:
                self.sidebar_image_label.setText("🚫 Image failed to load.")
                self.sidebar_image_label.setStyleSheet("color: red; border: 1px solid #555;")
        else:
            self.sidebar_image_label.clear()
            self.sidebar_image_label.setText("No Image Available")
            self.sidebar_image_label.setStyleSheet("color: white; border: 1px solid #555;")

    def refresh_ui(self):
        # Clear existing widgets from the grid layout
        while self.container_grid_layout.count():
            item = self.container_grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        # Reset grid position counters
        self.grid_row = 0
        self.grid_col = 0

        # Clear current inventory and fetch fresh data from DB
        self.inventory = FunkoDB.get_all_funkos()

        # Add all Funkos back to UI grid
        for funko in self.inventory:
            self.add_pop_to_ui(funko)

        # Disable edit/delete buttons after refresh
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.current_pop = None
        self.sidebar_label.setText("POP DETAILS (Click a Pop)")
        self.sidebar_image_label.clear()
        self.details_label.setText("Name:\nSeries:\nValue:")

    def delete_funko(self):
        from PyQt5.QtWidgets import QMessageBox

        if hasattr(self, "current_pop") and self.current_pop:
            confirm = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete '{self.current_pop.name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                FunkoDB.delete_funko(self.current_pop.id)
                print(f"Deleted: {self.current_pop.name}")
                self.current_pop = None
                self.edit_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                self.refresh_ui()
        else:
            QMessageBox.information(self, "No Pop Selected", "Please select a Funko to delete.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Home()
    main_window.show()
    sys.exit(app.exec_())
