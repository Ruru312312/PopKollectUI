from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from funko_pop import FunkoPop
from funko_db import FunkoDB

# Dialog for editing Funko Pop details
class PopDetailsDialog(QDialog):
    def __init__(self, funko: FunkoPop, parent=None):
        super().__init__(parent)
        self.funko = funko
        self.setWindowTitle("Edit Funko Details")
        self.setMinimumWidth(300)

        from PyQt5.QtCore import Qt
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)


        layout = QVBoxLayout()

        # Input fields (editable by default)
        self.barcode_field = QLineEdit(funko.barcode)
        self.name_field = QLineEdit(funko.name)
        self.series_field = QLineEdit(funko.series)
        self.item_number_field = QLineEdit(funko.item_number)
        self.year_field = QLineEdit(funko.year)
        self.value_field = QLineEdit(str(funko.market_value))

        self.barcode_field.setToolTip("A valid barcode is required to fetch your Pop's market value.")
        self.year_field.setToolTip("The Pop's release year influences its market value. Please input its actual release year for an accurate market value.")
        self.value_field.setToolTip("Feel free to edit this value if your Pop is not yet on PopKollect's list of Pops used for market value computations.")


        layout.addWidget(QLabel("Barcode:"))
        layout.addWidget(self.barcode_field)
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_field)
        layout.addWidget(QLabel("Series:"))
        layout.addWidget(self.series_field)
        layout.addWidget(QLabel("Item #:"))
        layout.addWidget(self.item_number_field)
        layout.addWidget(QLabel("Year:"))
        layout.addWidget(self.year_field)
        layout.addWidget(QLabel("Market Value:"))
        layout.addWidget(self.value_field)

        # Save and Cancel buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connect buttons
        self.save_btn.clicked.connect(self.save_changes)
        self.cancel_btn.clicked.connect(self.reject)  # Just close dialog without saving

    def save_changes(self):
        # Save changes to the funko object and database
        self.funko.barcode = self.barcode_field.text()
        self.funko.name = self.name_field.text()
        self.funko.series = self.series_field.text()
        self.funko.item_number = self.item_number_field.text()
        self.funko.year = self.year_field.text()
        self.funko.market_value = float(self.value_field.text())

        FunkoDB.update_funko(self.funko)
        self.accept()  # Close dialog with Accepted result
