# class FunkoPop:
#     """Represents a collectible Funko Pop item with essential details."""
    
#     def __init__(self, name: str, series: str, barcode: str, market_value: float, image_path: str = "", 
#                  itemNo: str = "", releaseYear: str = ""): # <-- NEW PARAMETERS
#         self.name = name
#         self.series = series
#         self.barcode = barcode
#         self.market_value = market_value
#         self.image_path = image_path
#         self.itemNo = itemNo         # <-- New
#         self.releaseYear = releaseYear # <-- New

    # def get_info(self) -> dict:
    #     """
    #     Returns the Pop's information as a DICTIONARY. 
    #     """
    #     return {
    #         'name': self.name,
    #         'series': self.series,
    #         'barcode': self.barcode,
    #         'market_value': f"{self.market_value:.2f}",
    #         'image_path': self.image_path,
    #         'item_no': self.itemNo,      # <-- New
    #         'release_year': self.releaseYear # <-- New
    #     }

#     def update_value(self, new_value: float):
#         """Updates the market value of the Funko Pop."""
#         if new_value >= 0:
#             self.market_value = new_value
#             print(f"Value for '{self.name}' updated to ${new_value:.2f}")
#         else:
#             print("Error: Market value cannot be negative.")



from dataclasses import dataclass, field
from typing import Optional

# funko pop class with multiple constructors simulated via classmethods
class FunkoDB:
    @staticmethod
    def update_funko(funko):
        print(f"[Mock DB] Updating Funko: {funko.name} (ID: {funko.id})")

@dataclass
class FunkoPop:
    id: int = -1
    barcode: Optional[str] = None
    name: Optional[str] = None
    series: Optional[str] = None
    item_number: Optional[str] = None
    year: Optional[str] = None
    variant: Optional[str] = None
    exclusive: Optional[str] = None
    condition: Optional[str] = None
    purchase_price: Optional[str] = None
    market_value: float = 0.0
    firestore_id: Optional[str] = None
    image_path: Optional[str] = None


    # Simulating overloaded constructors with classmethods
    @classmethod
    def from_basic(cls, barcode, name, series, item_number):
        # print("Funko.from_basic() -1- was called")
        return cls(barcode=barcode, name=name, series=series, item_number=item_number)

    @classmethod
    def from_detailed(cls, id, barcode, name, series, item_number, market_value, year, image_path):
        # print("Funko.from_detailed() -2- was called")
        return cls(id=id, barcode=barcode, name=name, series=series, item_number=item_number,
                   market_value=market_value, year=year, image_path=image_path)

    @classmethod
    def from_firebase_funkos(cls, barcode, name, market_value, year):
        # print("Funko.from_firebase_funkos() -3- was called")
        return cls(barcode=barcode, name=name, market_value=market_value, year=year)

    @classmethod
    def from_sqlite(cls, barcode, name, series, item_number, market_value, year, image_path):
        # print("Funko.from_sqlite() -4- was called")
        return cls(barcode=barcode, name=name, series=series, item_number=item_number,
                   market_value=market_value, year=year, image_path=image_path)

    def get_info(self) -> dict:
        """
        Returns the Pop's information as a DICTIONARY. 
        """
        return {
            'name': self.name,
            'series': self.series,
            'barcode': self.barcode,
            'market_value': f"{self.market_value:.2f}",
            'image_path': self.image_path,
            'item_number': self.item_number,
            'year': self.year
        }
    
    # Getters and setters with optional update calls
    def get_firestore_id(self):
        return self.firestore_id

    def set_firestore_id(self, firestore_id):
        self.firestore_id = firestore_id

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_barcode(self):
        return self.barcode

    def set_barcode(self, barcode):
        self.barcode = barcode

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name
        FunkoDB.update_funko(self)
        print(f"Updated Funko Name of ID: {self.id}\n")

    def get_series(self):
        return self.series

    def set_series(self, series):
        self.series = series
        FunkoDB.update_funko(self)
        print(f"Updated Funko Series of ID: {self.id}\n")

    def get_item_number(self):
        return self.item_number

    def set_item_number(self, item_number):
        self.item_number = item_number
        FunkoDB.update_funko(self)
        print(f"Updated Funko Item Number of ID: {self.id}\n")

    def get_year(self):
        return self.year

    def set_year(self, year):
        self.year = year

    def get_variant(self):
        return self.variant

    def set_variant(self, variant):
        self.variant = variant

    def get_exclusive(self):
        return self.exclusive

    def set_exclusive(self, exclusive):
        self.exclusive = exclusive

    def get_condition(self):
        return self.condition

    def set_condition(self, condition):
        self.condition = condition

    def get_purchase_price(self):
        return self.purchase_price

    def set_purchase_price(self, purchase_price):
        self.purchase_price = purchase_price

    def get_market_value(self):
        print("Funko.get_market_value() was called")
        return self.market_value

    def set_market_value(self, market_value):
        print("Funko.set_market_value() was called")
        self.market_value = market_value
        print("--- Funko.set_market_value() ended ---")

# Example usage:
if __name__ == "__main__":
    f1 = Funko.from_basic("123456", "Batman", "DC Series", "001")
    f1.set_name("Batman Updated")
    f1.set_market_value(45.99)
    print(f"Market Value: {f1.get_market_value()}")
