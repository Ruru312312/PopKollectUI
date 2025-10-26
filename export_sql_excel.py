import sqlite3
import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QMessageBox

def export_sql_excel(self):
    try:
        # Connect to your database
        conn = sqlite3.connect("funko_pops.db")

        # Get all table names in the database
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)

        if tables.empty:
            QMessageBox.warning(self, "No Tables Found", "The database contains no tables.")
            conn.close()
            return

        # Ask user where to save the Excel file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")

        if not file_path:
            QMessageBox.warning(self, "Export Cancelled", "No file was saved.")
            conn.close()
            return

        # Create Excel writer
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Loop through each table and write it to a separate sheet
            for table_name in tables['name']:
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                df.to_excel(writer, sheet_name=table_name, index=False)

        conn.close()

        QMessageBox.information(self, "Export Successful", f"All tables exported successfully to:\n{file_path}")

    except Exception as e:
        QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")
