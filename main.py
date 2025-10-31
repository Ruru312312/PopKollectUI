import sys, subprocess
import os # NEW: Import os for file checking
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QSplitter, QPushButton,
    QScrollArea, QDialog, QGridLayout, QSizePolicy, QSpacerItem, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon # NEW: Import QIcon for the info symbol

# --- Import the separated classes ---
from funko_pop import FunkoPop
from clickable_container import ClickableContainer
from add_item_dialog import AddItemDialog
from pop_details_dialog import PopDetailsDialog
from funko_db import FunkoDB
from firebase_db import FirebaseDB
from sync_app import SyncApp
from sync_firebase import SyncFirebase


FunkoDB.create_table()  # Ensure the database table exists

# Main Application Window
class Home(QWidget):

    def __init__(self):
        print("-----Home.__init__() was called-----")
        super().__init__()
        self.setWindowTitle("PopKollect")
        # Increase initial window width to accommodate 5 columns and sidebars
        self.setGeometry(100, 100, 1400, 800) 
        
        self.current_pop = None
        self.inventory = []
        self.grid_row = 0
        self.grid_col = 0
        self.max_cols = 5
        self.initUI()
        self.refresh_ui()
        print("-----Home.__init__() was completed-----")
        
    def setup_info_icon(self, label_widget, tooltip_text):
        """Sets up a QLabel to display a generic info icon and a tooltip."""
        
        # Using Unicode info symbol as a reliable icon replacement
        label_widget.setText("ⓘ") 
        label_widget.setStyleSheet("color: #FFFF00; font-weight: bold;")
        
        # Set the tooltip text
        label_widget.setToolTip(tooltip_text)
        
        # Ensure the label is small and fixed size
        label_widget.setFixedSize(20, 20) 
        label_widget.setAlignment(Qt.AlignCenter)

    def initUI(self):
        print("-----Home.initUI() was called-----")
        main_splitter = QSplitter(Qt.Horizontal)

        # --- Section 1: Logo and Add Button (Left) ---
        left_frame = QFrame(self)
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setStyleSheet("background-color: #333; color: white;")
        left_frame.setFixedWidth(150)

        left_layout = QVBoxLayout(left_frame)
        # logo_label = QLabel("logo\luffy.jpg", left_frame)
        # logo_label.setAlignment(Qt.AlignCenter)
        # logo_label.setStyleSheet("font-size: 24px; font-weight: bold; border: 2px solid grey; padding: 10px;")

        logo_label = QLabel(left_frame)
        logo_pixmap = QPixmap("logo/luffy.jpg")
        logo_pixmap = logo_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("border: 2px solid grey; padding: 10px;")
        
        # --- BUTTONS SECTION ---

        add_button = QPushButton("Add New Pop", left_frame)
        add_button.setStyleSheet("""
            /* Default (Idle) State */
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                padding: 10px; 
                border-radius: 5px;
            }
            /* Pressed State: Darken color and shift text down/right */
            QPushButton:pressed {
                background-color: #388E3C; /* A darker green */
                padding-left: 9px;  /* Shift content slightly */
                padding-top: 11px;
            }
        """)
        add_button.clicked.connect(self.open_add_item_dialog)

        
        sync_button = QPushButton("Fetch Market Values", left_frame)
        sync_button.setStyleSheet("""
            /* Default (Idle) State */
            QPushButton {
                background-color: #000080; 
                color: white; 
                padding: 10px; 
                border-radius: 5px;
            }
            /* Pressed State: Darken color and shift text down/right */
            QPushButton:pressed {
                background-color: #388E3C; /* A darker green */
                padding-left: 9px;  /* Shift content slightly */
                padding-top: 11px;
            }
        """)
        sync_button.setToolTip("Fetches updated market values from the online database (ONE USE PER DAY).")
        sync_button.clicked.connect(SyncFirebase.sync_firebase)

        update_button = QPushButton("Sync Market Values", left_frame)
        update_button.setStyleSheet("""
            /* Default (Idle) State */
            QPushButton {
                background-color: #FF7F50; 
                color: white; 
                padding: 10px; 
                border-radius: 5px;
            }
            /* Pressed State: Darken color and shift text down/right */
            QPushButton:pressed {
                background-color: #388E3C; /* A darker green */
                padding-left: 9px;  /* Shift content slightly */
                padding-top: 11px;
            }
        """)
        update_button.setToolTip("Syncs your local collection with the latest market values fetched from the online database.")
        update_button.clicked.connect(self.sync_app)

        export_button = QPushButton("Export to Excel", left_frame)
        export_button.setStyleSheet("background-color: #00A86B; color: white; padding: 8px; border-radius: 5px;")
        export_button.setToolTip("Export data to Excel File format")
        export_button.clicked.connect(self.export_sql_excel)


        # Add buttons to the layout
        left_layout.addWidget(logo_label)
        left_layout.addSpacing(20)
        left_layout.addWidget(add_button)
        left_layout.addSpacing(15)
        left_layout.addWidget(sync_button)
        left_layout.addWidget(update_button)
        left_layout.addWidget(export_button)
        left_layout.addStretch(1)

        main_splitter.addWidget(left_frame)

        # --- Section 2: Containers (Middle) ---
        middle_frame = QFrame(self)
        middle_frame.setMinimumWidth(1250)
        middle_frame.setFrameShape(QFrame.StyledPanel)
        middle_frame.setStyleSheet("background-color: #222;")
        self.scroll_area = QScrollArea(middle_frame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scroll_content_widget = QWidget()
        self.container_grid_layout = QGridLayout(self.scroll_content_widget) 
        
        self.container_grid_layout.setContentsMargins(20, 20, 20, 20)
        self.container_grid_layout.setSpacing(20) 

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

        # --- Section 3: Sidebar (Right - UPDATED to QGridLayout for Details) ---
        right_frame = QFrame(self)
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setStyleSheet("background-color: #333; color: white;")
        right_frame.setFixedWidth(400)
        
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

        
        # Details Frame and Grid Layout
        details_frame = QFrame(right_frame)
        details_layout = QGridLayout(details_frame)
        details_frame.setFixedWidth(380)
        
        # --- Create Detail Labels and Info Icons ---
        # 0: Barcode Label and Icon
        self.barcode_label = QLabel("Barcode: --")
        self.barcode_icon = QLabel(details_frame)
        self.setup_info_icon(self.barcode_icon, "The barcode is required to fetch market values from the online database.")
        details_layout.addWidget(self.barcode_label, 0, 0)
        details_layout.addWidget(self.barcode_icon, 0, 1)
        
        # 1: Name Label
        self.name_label = QLabel("Name: --")
        details_layout.addWidget(self.name_label, 1, 0, 1, 2)
        
        # 2: Series Label
        self.series_label = QLabel("Series: --")
        details_layout.addWidget(self.series_label, 2, 0, 1, 2)
        
        # 3: Item Number Label
        self.item_number_label = QLabel("Item Number: --")
        details_layout.addWidget(self.item_number_label, 3, 0, 1, 2)
        
        # 4: Release Year Label and Icon
        self.year_label = QLabel("Release Year: --")
        self.year_icon = QLabel(details_frame)
        self.setup_info_icon(self.year_icon, "The release year influences market value calculations. Please ensure it's accurate.")
        details_layout.addWidget(self.year_label, 4, 0)
        details_layout.addWidget(self.year_icon, 4, 1)

        # 5: Market Value Label
        self.value_label = QLabel("Market Value: --")
        self.value_icon = QLabel(details_frame)
        self.setup_info_icon(self.value_icon, "You may edit this value manually if your Pop is not listed in the online database.")
        details_layout.addWidget(self.value_label, 5, 0)
        details_layout.addWidget(self.value_icon, 5, 1)
        
        # 6: invis Label
        self.invis_label = QLabel("")
        self.invis_label.setStyleSheet("color: red; font-weight: bold; margin-top: 10px;")
        details_layout.addWidget(self.invis_label, 6, 0, 1, 2)

        # Configure the grid columns
        details_layout.setColumnStretch(0, 1) # Label column gets most space
        details_layout.setColumnStretch(1, 0) # Icon column is tight
        
        # Add the new details frame to the main right layout
        right_layout.addWidget(details_frame)
        right_layout.addStretch(1) # Stretch ensures layout is pushed up

        # edit and delete buttons
        core_buttons_frame = QFrame()
        core_layout = QHBoxLayout(core_buttons_frame)

        self.edit_button = QPushButton("Edit")
        self.edit_button.setStyleSheet("""
            /* Default (Idle) State */
            QPushButton {
                background-color: #808080; 
                color: white; 
                padding: 10px; 
                border-radius: 5px;
            }
            /* Pressed State: Darken color and shift text down/right */
            QPushButton:pressed {
                background-color: #696969; 
                padding-left: 9px;  
                padding-top: 11px;
            }
        """)
        self.edit_button.setToolTip("Edit the selected Pop's details")
        self.edit_button.setEnabled(False) 

        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet("""
            /* Default (Idle) State */
            QPushButton {
                background-color: #FF0000; 
                color: white; 
                padding: 10px; 
                border-radius: 5px;
            }
            /* Pressed State: Darken color and shift text down/right */
            QPushButton:pressed {
                background-color: #B22222; 
                padding-left: 9px;  
                padding-top: 11px;
            }
        """)
        self.delete_button.setToolTip("Delete the selected Pop from your collection")
        self.delete_button.setEnabled(False) 

        core_layout.addWidget(self.edit_button)
        core_layout.addWidget(self.delete_button)

        # add buttons to the right sidebar
        right_layout.addWidget(core_buttons_frame)
        right_layout.addStretch(1)

        main_splitter.addWidget(right_frame)

        # Set initial sizes.
        main_splitter.setSizes([150, 850, 400]) 
        
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

        # BUTTON FUNCTIONS
        self.edit_button.clicked.connect(self.open_edit_pop_dialog)
        self.delete_button.clicked.connect(self.delete_funko)
        print("-----Home.initUI() has completed-----")

#open_edit_pop_dialog starts here
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
            QMessageBox.information(self, "No Pop Selected", "Please select a Funko to edit.")
#open_edit_pop_dialog ends here

#open_add_item_dialog starts here
    def open_add_item_dialog(self):
        dialog = AddItemDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_pop = dialog.new_pop
            if new_pop:
                self.refresh_ui()
#open_add_item_dialog ends here

#add_pop_to_ui starts here
    def add_pop_to_ui(self, pop_object: FunkoPop):
        container = ClickableContainer(pop_object, self.scroll_content_widget)
        container.clicked.connect(self.FBpopChecker)
        container.clicked.connect(self.display_pop_details)
        

        self.container_grid_layout.addWidget(
            container, self.grid_row, self.grid_col
        )

        self.grid_col += 1
        if self.grid_col >= self.max_cols:
            self.grid_col = 0
            self.grid_row += 1
#add_pop_to_ui ends here

#testFunctionPopFinder
    def FBpopChecker (self, pop_object: FunkoPop):
        print ("----------FBpopCheckerCalled------------")

        firebase_funkos = FirebaseDB.get_all_funkos()
        current_funkos = pop_object
        PopFoundInDB = False

        for firebase_funko in firebase_funkos:
            if current_funkos.barcode == firebase_funko.barcode:
                if current_funkos.year == firebase_funko.year:
                    print(current_funkos.name)
                    PopFoundInDB = True
                    print ("Pop foound in database")
                    continue
        
        if not PopFoundInDB:
            print("Pop was not found in database")
        return PopFoundInDB
             
        
        


#testFunctionPopFinder

#display_pop_details starts here
    
    def display_pop_details(self, pop_object: FunkoPop):
        
        invisValue = self.FBpopChecker(pop_object)
        
        self.current_pop = pop_object
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.sidebar_label.setText(f"Details for: {pop_object.name}")
        info = pop_object.get_info()

        # UPDATED: Set text for individual labels
        self.barcode_label.setText(f"Barcode: {info['barcode']}")
        self.name_label.setText(f"Name: <b>{info['name']}</b>")
        self.series_label.setText(f"Series: {info['series']}")
        self.item_number_label.setText(f"Item Number: {info['item_number']}")
        self.year_label.setText(f"Release Year: {info['year']}")
        self.value_label.setText(f"Market Value: <b>${info['market_value']}</b>")
        
        if invisValue == True:
            varText = ""
        if invisValue == False:
            varText = "POP NOT IN DATABASE"
        
        self.invis_label.setText(varText)
        # current_barcode = info['barcode']
        
        
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
#display_pop_details ends here

#refresh_ui starts here
    def refresh_ui(self):
        print("Home.refresh_ui() was called")
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

        # Disable edit/delete buttons after refresh and clear sidebar labels
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.current_pop = None
        self.sidebar_label.setText("POP DETAILS (Click a Pop)")
        self.sidebar_image_label.clear()
        
        # Reset individual detail labels
        self.barcode_label.setText("Barcode: --")
        self.name_label.setText("Name: --")
        self.series_label.setText("Series: --")
        self.item_number_label.setText("Item Number: --")
        self.year_label.setText("Release Year: --")
        self.value_label.setText("Market Value: --")
        
#refresh_ui ends here

#delete_funko starts here
    def delete_funko(self):
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
#delete_funko ends

# sync_app starts here
    def sync_app(self):
        import os
        from PyQt5.QtWidgets import QMessageBox

        DB_FILE_NAME = "firebase_funkos.db"
        
        print("Update button clicked")
        print("Home.sync_app() was called")

        # CHECK 1: Check for the database file in the current directory
        if not os.path.exists(DB_FILE_NAME):
            QMessageBox.warning(
                self, 
                "Update Failed", 
                f"Cannot sync market values. Please click the \"Fetch Market Values\" button first."
            )
            print(f"Error: {DB_FILE_NAME} not found. Update aborted.")
            return # Stop execution if the file is missing

        # CHECK 2 (Optional but recommended): Check for internet connection if possible before proceeding
        # (Assuming SyncApp.sync_market_values() handles the actual internet connection check)

        # 3. If the file is found, proceed with the update logic
        SyncApp.sync_market_values()
        
        self.refresh_ui()
        print("----- Home.sync_app() has completed. -----")
# sync_app ends here

# export_sql_excel starts here
    def export_sql_excel(self):
        import sqlite3
        import pandas as pd
        from PyQt5.QtWidgets import QFileDialog, QMessageBox

        try:
            conn = sqlite3.connect("funko_pops.db")
            tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)

            if tables.empty:
                QMessageBox.warning(self, "No Tables Found", "The database contains no tables.")
                conn.close()
                return

            file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")

            if not file_path:
                conn.close()
                return

            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for table_name in tables['name']:
                    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                    df.to_excel(writer, sheet_name=table_name, index=False)

            conn.close()
            QMessageBox.information(self, "Export to Excel is Successful", f"Check your Excel file here:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")
# export_sql_excel ends here


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QToolTip {
            background-color: #444; 
            color: #FFFF00; 
            padding: 5px; 
            border: 1px solid #777;
            border-radius: 3px;
        }
    """)


    main_window = Home()
    main_window.show()
    sys.exit(app.exec_())