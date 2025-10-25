import os
import traceback
from typing import List, Optional

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except Exception:
    FIREBASE_AVAILABLE = False

from funko_pop import FunkoPop as Funko

# Firestore connection
class FirestoreConnection:
    """
    Python port of your Java FirestoreConnection.
    Usage:
      conn = FirestoreConnection()
      funkos = conn.get_all_funkos()
      conn.update_market_value(doc_id, 12.34)
    """

    # Hardcoding the service account path here
    SERVICE_ACCOUNT_PATH = "funkokenny-5585a-firebase-adminsdk-fbsvc-aa0164b777.json"  # Update with your actual file path
    DATABASE_URL = "https://funkokenny-5585a-default-rtdb.asia-southeast1.firebasedatabase.app"  # Update with your actual Firebase Database URL if necessary

    def __init__(self):
        self.db = None
        try:
            if not FIREBASE_AVAILABLE:
                raise RuntimeError("firebase-admin package not installed (pip install firebase-admin)")

            if not os.path.exists(self.SERVICE_ACCOUNT_PATH):
                raise FileNotFoundError(f"Service account file not found: {self.SERVICE_ACCOUNT_PATH}")

            cred = credentials.Certificate(self.SERVICE_ACCOUNT_PATH)

            # Initialize app only if not already initialized
            try:
                firebase_admin.get_app()
            except ValueError:
                # pass an options dict only if database_url provided
                options = {"databaseURL": self.DATABASE_URL} if self.DATABASE_URL else None
                if options:
                    firebase_admin.initialize_app(cred, options)
                else:
                    firebase_admin.initialize_app(cred)

            # Firestore client
            self.db = firestore.client()

        except Exception as e:
            print("Failed to initialize FirestoreConnection:", e)
            traceback.print_exc()

        print("FirestoreConnection() was called")

    # Optional: add a Funko document to Firestore (kept similar to your Java commented method)
    def add_funko(self, funko: Funko) -> Optional[str]:
        """
        Add a Funko object to the 'funkos' collection.
        Returns the generated document id or None on failure.
        """
        if self.db is None:
            print("Firestore not initialized")
            return None
        try:
            data = funko.to_dict() if hasattr(funko, "to_dict") else funko.__dict__
            ref = self.db.collection("funkos").add(data)
            doc_ref = ref[1] if isinstance(ref, tuple) else ref
            doc_id = None
            if hasattr(ref, "id"):
                doc_id = ref.id
            else:
                try:
                    doc_id = ref[0].id
                except Exception:
                    try:
                        doc_id = ref[1].id
                    except Exception:
                        pass
            if doc_id:
                try:
                    setattr(funko, "firestore_id", doc_id)
                except Exception:
                    pass
            print("Added funko with id:", doc_id)
            return doc_id
        except Exception as e:
            print("Failed to add funko:", e)
            traceback.print_exc()
            return None

    def update_market_value(self, doc_id: str, market_value: float):
        """Update the marketValue field for the document with doc_id."""
        print("FirestoreConnection.update_market_value() was called")
        if self.db is None:
            print("Firestore not initialized")
            return
        try:
            write_result = self.db.collection("funkos").document(doc_id).update({"marketValue": market_value})
            update_time = getattr(write_result, "update_time", None)
            print(f"✅ Updated {doc_id} at {update_time}")
        except Exception as e:
            print(f"❌ Failed to update {doc_id}: {e}")
            traceback.print_exc()

    def get_all_funkos(self) -> List[Funko]:
        """
        Retrieve all documents from the 'funkos' collection and convert them to Funko instances.
        Each returned Funko will have an attribute `firestore_id` set to the document id.
        """
        print("FirestoreConnection.get_all_funkos() was called")
        funkos: List[Funko] = []
        if self.db is None:
            print("Firestore not initialized")
            return funkos
        try:
            docs = self.db.collection("funkos").get()
            for doc in docs:
                data = doc.to_dict() or {}
                f = Funko(
                    id=None,
                    name=data.get("name") or "",
                    series=data.get("series") or "",
                    item_number=data.get("itemNumber") or "",
                    year=data.get("year") or "",
                    barcode=data.get("barcode") or "",
                    market_value=float(data.get("marketValue") or 0.0)
                    # image_path=data.get("image_path") or data.get("image") or ""
                    #notes=data.get("notes") or ""
                )
                try:
                    setattr(f, "firestore_id", doc.id)
                except Exception:
                    pass
                print(f"Loaded Funko: {f.name}, Document ID: {getattr(f, 'firestore_id', None)}")
                funkos.append(f)
        except Exception as e:
            print("Failed to load funkos from Firestore:", e)
            traceback.print_exc()
        return funkos
