import json
import os
from prettytable import PrettyTable

class PortfolioManager:
    def __init__(self, filename="portfolio.json"):
        self.filename = filename
        self.holdings = self._load_holdings()

    def _load_holdings(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode {self.filename}. Starting with empty portfolio.")
                    return []
        return []

    def _save_holdings(self):
        with open(self.filename, 'w') as f:
            json.dump(self.holdings, f, indent=4)

    def add_holding(self, symbol, quantity, asset_type):
        """Adds a new stock/crypto holding or updates an existing one."""
        for holding in self.holdings:
            if holding["symbol"].upper() == symbol.upper() and holding["type"].lower() == asset_type.lower():
                holding["quantity"] += quantity
                print(f"Updated {symbol} quantity to {holding['quantity']}")
                self._save_holdings()
                return

        self.holdings.append({
            "symbol": symbol.upper(),
            "quantity": quantity,
            "type": asset_type.lower()
        })
        print(f"Added {quantity} of {symbol} ({asset_type}) to portfolio.")
        self._save_holdings()

    def remove_holding(self, symbol, asset_type):
        """Removes a holding from the portfolio."""
        initial_count = len(self.holdings)
        self.holdings = [
            h for h in self.holdings
            if not (h["symbol"].upper() == symbol.upper() and h["type"].lower() == asset_type.lower())
        ]
        if len(self.holdings) < initial_count:
            print(f"Removed {symbol} ({asset_type}) from portfolio.")
            self._save_holdings()
        else:
            print(f"{symbol} ({asset_type}) not found in portfolio.")

    def get_all_holdings(self):
        """Returns all holdings."""
        return self.holdings

    def display_portfolio_summary(self, api_client_instance): # Renamed to avoid conflict with class name
        """Fetches current prices and displays a summary of the portfolio."""
        print("\n--- Your Portfolio Summary ---")
        if not self.holdings:
            print("Portfolio is empty. Add some holdings!")
            return

        total_portfolio_value = 0
        table = PrettyTable()
        table.field_names = ["Symbol", "Type", "Quantity", "Current Price", "Value", "Daily Change (%)"]

        for holding in self.holdings:
            symbol = holding["symbol"]
            quantity = holding["quantity"]
            asset_type = holding["type"]
            current_price = None
            daily_change_percent = "N/A"

            if asset_type == "stock":
                data = api_client_instance.get_stock_price(symbol)
                if data:
                    current_price = data['price']
                    daily_change_percent = data['change_percent']
            elif asset_type == "crypto":
                coingecko_id_map = {"BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "DOGE": "dogecoin"}
                coingecko_id = coingecko_id_map.get(symbol.upper(), symbol.lower())
                data = api_client_instance.get_crypto_price(coingecko_id)
                if data:
                    current_price = data['price']

            if current_price is not None:
                value = current_price * quantity
                total_portfolio_value += value
                table.add_row([symbol, asset_type.capitalize(), quantity, f"${current_price:.2f}", f"${value:.2f}", daily_change_percent])
            else:
                table.add_row([symbol, asset_type.capitalize(), quantity, "N/A", "N/A", "N/A"])

        print(table)
        print(f"\nTotal Portfolio Value: ${total_portfolio_value:.2f}")
        print("-" * 30)

# This line is for debugging only and should not be in a module file
if __name__ == "__main__":
    print("PortfolioManager class defined.")