from firebase_db import FirebaseDB
from firestore_connection import FirestoreConnection

# Sync Firebase funkos into local firebase_funkos.db
class SyncFirebase:
    def sync_firebase():
        # 1. Ensure local DB table exists
        FirebaseDB.create_table()
        print("✅ Ensured firebase_funkos.db table exists"  )

        # 2. Fetch funkos from Firebase
        connection = FirestoreConnection()  # Initializes Firebase connection
        firebase_funkos = connection.get_all_funkos()  # Gets Funkos from Firestore
    
        # 3. Sync each Funko to firebase_funkos.db
        for f in firebase_funkos:
            FirebaseDB.upsert_funko(f.barcode, f.name, f.market_value, f.year)
            print(f"✅ Synced Funko Pop: {f.name}")

        print("✅ Synced Firebase funkos into firebase_funkos.db")

if __name__ == "__main__":
    sync_firebase()
