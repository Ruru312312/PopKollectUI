import sqlite3
from typing import List
from funko_pop import FunkoPop


class FunkoDB:
    DB_PATH = "funko_pops.db"

    @staticmethod
    def create_table():

        print("FunkoDB.create_table() was called")
        
        sql = """
        CREATE TABLE IF NOT EXISTS funko_pops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT,
            name TEXT NOT NULL,
            series TEXT NOT NULL,
            item_number TEXT NOT NULL,
            market_value REAL,
            year TEXT
        );
        """
        with sqlite3.connect(FunkoDB.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()

    @staticmethod
    def add_funko(funko: FunkoPop) -> int:
        print("FunkoDB.add_funko() was called")
        sql = """
        INSERT INTO funko_pops (barcode, name, series, item_number, market_value, year)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        with sqlite3.connect(FunkoDB.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                funko.barcode,
                funko.name,
                funko.series,
                funko.item_number,
                funko.market_value,
                funko.year
            ))
            conn.commit()
            return cursor.lastrowid  # Return the auto-generated ID

    @staticmethod
    def get_all_funkos() -> List[FunkoPop]:
        print("FunkoDB.get_all_funkos() was called")
        funkos = []
        sql = "SELECT * FROM funko_pops"
        with sqlite3.connect(FunkoDB.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                funko = FunkoPop.from_detailed(
                    id=row[0],
                    barcode=row[1],
                    name=row[2],
                    series=row[3],
                    item_number=row[4],
                    market_value=row[5],
                    year=row[6]
                )
                funkos.append(funko)
        return funkos

    @staticmethod
    def update_funko(funko: FunkoPop):
        
        print("FunkoDB.update_funko() was called")

        print(f"Funko ID in FunkoDB: {funko.id}")
        sql = """
        UPDATE funko_pops SET barcode=?, name=?, series=?, item_number=?, market_value=?, year=?
        WHERE id=?
        """
        with sqlite3.connect(FunkoDB.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                funko.barcode,
                funko.name,
                funko.series,
                funko.item_number,
                funko.market_value,
                funko.year,
                funko.id
            ))
            conn.commit()
            print("Funko was updated successfully")

    @staticmethod
    def delete_funko(funko_id: int):
        print("FunkoDB.delete_funko() was called")
        sql = "DELETE FROM funko_pops WHERE id=?"
        with sqlite3.connect(FunkoDB.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (funko_id,))
            conn.commit()

    @staticmethod
    def update_market_value_by_barcode_and_year(barcode: str, year: str, market_value: float):
        print("FunkoDB.update_market_value_by_barcode_and_year() was called")
        sql = "UPDATE funko_pops SET market_value=? WHERE barcode=? AND year=?"
        with sqlite3.connect(FunkoDB.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (market_value, barcode, year))
            conn.commit()


# Example usage:
if __name__ == "__main__":
    FunkoDB.create_table()

    # Create a Funko object using your classmethods
    new_funko = FunkoPop.from_basic("123456789", "Spider-Man", "Marvel", "SP001")
    new_funko.market_value = 25.50
    new_funko.year = "2023"

    # Add Funko to DB and get the assigned ID
    new_funko.id = FunkoDBs.add_funko(new_funko)
    print(f"Added Funko with ID: {new_funko.id}")

    # Retrieve all Funkos from DB
    all_funkos = FunkoDB.get_all_funkos()
    print(f"Retrieved {len(all_funkos)} Funkos from DB")

    # Update Funko info
    new_funko.set_market_value(30.00)
    FunkoDB.update_funko(new_funko)

    # Delete Funko by ID
    # FunkoDB.delete_funko(new_funko.id)
