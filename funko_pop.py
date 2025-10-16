# funko_pop.py (UPDATED)

class FunkoPop:
    """Represents a collectible Funko Pop item with essential details."""
    
    def __init__(self, name: str, series: str, barcode: str, market_value: float, image_path: str = "", 
                 itemNo: str = "", releaseYear: str = ""): # <-- NEW PARAMETERS
        self.name = name
        self.series = series
        self.barcode = barcode
        self.market_value = market_value
        self.image_path = image_path
        self.itemNo = itemNo         # <-- New
        self.releaseYear = releaseYear # <-- New

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
            'item_no': self.itemNo,      # <-- New
            'release_year': self.releaseYear # <-- New
        }

    def update_value(self, new_value: float):
        """Updates the market value of the Funko Pop."""
        if new_value >= 0:
            self.market_value = new_value
            print(f"Value for '{self.name}' updated to ${new_value:.2f}")
        else:
            print("Error: Market value cannot be negative.")