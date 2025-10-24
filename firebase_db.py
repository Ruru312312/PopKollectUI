import sqlite3, os
from funko_pop import FunkoPop
from typing import List

# SQLite database handler for Funko Pops fetched from Firebase
class FirebaseDB:
    URL = os.path.join(os.getcwd(), "firebase_funkos.db")

    @staticmethod
    def create_table():
        sql = '''
        CREATE TABLE IF NOT EXISTS firebase_funkos (
            barcode TEXT PRIMARY KEY,
            name TEXT,
            marketValue REAL,
            year TEXT
        );
        '''
        try:
            with sqlite3.connect(FirebaseDB.URL) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
        except sqlite3.Error as e:
            print(e)

    @staticmethod
    def upsert_funko(barcode, name, market_value, year):
        print(f"FirebaseDB.upsert_funko() was called")
        print(f"Funko Pop: {name}")

        sql = '''
        INSERT INTO firebase_funkos (barcode, name, marketValue, year)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(barcode) DO UPDATE SET
        name = excluded.name,
        marketValue = excluded.marketValue,
        year = excluded.year
        '''
        try:
            with sqlite3.connect(FirebaseDB.URL) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (barcode, name, market_value, year))
                conn.commit()
        except sqlite3.Error as e:
            print(e)

    @staticmethod
    def get_market_value(barcode):
        sql = "SELECT marketValue FROM firebase_funkos WHERE barcode = ?"
        try:
            with sqlite3.connect(FirebaseDB.URL) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (barcode,))
                row = cursor.fetchone()
                if row:
                    return row[0]
        except sqlite3.Error as e:
            print(e)
        return None  # return None if not found
    
    @staticmethod
    def get_all_funkos() -> List[FunkoPop]:
        print("FirebaseDB.get_all_funkos() was called")
        funkos = []
        sql = "SELECT * FROM firebase_funkos"
        with sqlite3.connect(FirebaseDB.URL) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                funko = FunkoPop.from_firebase_funkos(
                    barcode=row[0],
                    name=row[1],
                    market_value=row[2],
                    year=row[3]
                )
                funkos.append(funko)
        return funkos
