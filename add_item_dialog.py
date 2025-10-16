# add_item_dialog.py (UPDATED)

from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QMessageBox, 
    QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QLabel # <-- Added QLabel
)
from PyQt5.QtGui import QDoubleValidator, QRegularExpressionValidator
from PyQt5.QtCore import QRegularExpression, QLocale 

from funko_pop import FunkoPop 

class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Funko Pop")
        self.setModal(True)
        self.new_pop = None
        self.image_path = ""
        self.initUI()

    def initUI(self):
        form_layout = QFormLayout()

        # Input Fields
        self.name_input = QLineEdit(self)
        self.series_input = QLineEdit(self)
        self.barcode_input = QLineEdit(self)
        regex = QRegularExpression("[0-9]{1,15}") 
        validator = QRegularExpressionValidator(regex, self)
        self.barcode_input.setValidator(validator) 

        # --- NEW INPUT FIELDS ---
        self.item_no_input = QLineEdit(self)     
        self.release_year_input = QLineEdit(self)
        self.release_year_input.setMaxLength(4) # Limit year to 4 digits
        # ------------------------

        # Market Value (Read-Only)
        self.market_value_input = QLineEdit(self)
        # --- KEY CHANGE: Market value is NOT editable by the user ---
        self.market_value_input.setText("0.00") # Default value
        self.market_value_input.setReadOnly(True) 
        self.market_value_input.setStyleSheet("background-color: #555; color: white;") # Visual indicator
        # -------------------------------------------------------------

        # Image Selection Fields (Same as before)
        self.image_path_display = QLineEdit(self)
        self.image_path_display.setPlaceholderText("No image selected (Optional)")
        self.image_path_display.setReadOnly(True) 

        browse_button = QPushButton("Browse...", self)
        browse_button.clicked.connect(self.open_file_dialog)

        image_h_layout = QHBoxLayout()
        image_h_layout.addWidget(self.image_path_display)
        image_h_layout.addWidget(browse_button)

        # Adding fields to the layout
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Series:", self.series_input)
        form_layout.addRow("Barcode (numbers):", self.barcode_input)
        form_layout.addRow("Item Number:", self.item_no_input)      # <-- New Row
        form_layout.addRow("Release Year:", self.release_year_input) # <-- New Row
        form_layout.addRow("Market Value ($):", self.market_value_input) # Read-only
        form_layout.addRow("Image Path:", image_h_layout) 

        add_button = QPushButton("Create Pop", self)
        add_button.clicked.connect(self.create_and_accept)
        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(add_button)
        button_layout.addWidget(cancel_button)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        
    def open_file_dialog(self):
        # (Same as before)
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Pop Image", 
            "", 
            "Image Files (*.png *.jpg *.jpeg *.webp);;All Files (*)", 
            options=options
        )
        
        if file_path:
            self.image_path = file_path
            file_name = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
            self.image_path_display.setText(file_name)


    def create_and_accept(self):
        # 1. Collect and validate data
        name = self.name_input.text().strip()
        series = self.series_input.text().strip()
        barcode = self.barcode_input.text().strip()
        item_no = self.item_no_input.text().strip()     # <-- Collect new field
        release_year = self.release_year_input.text().strip() # <-- Collect new field
        
        # NOTE: market_value_str is read from the default/unchangeable text
        market_value_str = self.market_value_input.text().strip() 
        
        if not name or not series or not barcode or not item_no or not release_year:
            QMessageBox.warning(self, "Input Error", "All required fields must be filled out.")
            return

        try:
            # We still need a float value for the FunkoPop object
            market_value = float(market_value_str) 
        except ValueError:
            # This should only happen if the default text "0.00" is corrupted
            QMessageBox.warning(self, "Internal Error", "Could not process market value.")
            return

        # 2. Create the FunkoPop object
        self.new_pop = FunkoPop(
            name=name,
            series=series,
            barcode=barcode,
            market_value=market_value,
            image_path=self.image_path,
            itemNo=item_no,             # <-- Pass new field
            releaseYear=release_year    # <-- Pass new field
        )
        
        # 3. Close the dialog as accepted
        super().accept()