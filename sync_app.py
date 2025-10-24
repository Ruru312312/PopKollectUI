from funko_db import FunkoDB
from funko_pop import FunkoPop
from firebase_db import FirebaseDB

class SyncApp:
    def sync_market_values():
        print("-----SyncApp.sync_market_values() was called-----")
        
        # Step 1. Get the market values from the local database (firebase_funkos.db)
        # Get all Funkos from the database
        firebase_funkos = FirebaseDB.get_all_funkos()
        personal_funkos = FunkoDB.get_all_funkos()
        print(f"✅ Retrieved {len(firebase_funkos)} funkos from firebase_funkos.db")
        print(f"✅ Retrieved {len(personal_funkos)} funkos from funko_pops.db")

        # Step 2. Update the market value of the given Funko object based on barcode and year
        for personal_funko in personal_funkos:
            funko_was_found = False
            for firebase_funko in firebase_funkos:
                if personal_funko.barcode == firebase_funko.barcode:
                    if personal_funko.year == firebase_funko.year:
                        print("✅ "+personal_funko.name+" "+personal_funko.year+" was found in firebase_funkos.")
                        funko_was_found = True
                        personal_funko.market_value = firebase_funko.market_value
                    
                        # Update the market value in the local DB using the barcode and year
                        FunkoDB.update_market_value_by_barcode_and_year(personal_funko.barcode, personal_funko.year, personal_funko.market_value)
                    
                        print(personal_funko.name+" "+personal_funko.year+" was updated with the latest market values from firebase_funkos.db.")
                        break
        
            if not funko_was_found:
                print("❌ "+personal_funko.name+" "+personal_funko.year+" was not found in firebase_funkos.")
        print("-----SyncApp.sync_market_values() has completed.-----")
