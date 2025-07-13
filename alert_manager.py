import json
import os
import time
from prettytable import PrettyTable

class AlertManager:
    def __init__(self, filename="alerts.json"):
        self.filename = filename
        self.alerts = self._load_alerts()

    def _load_alerts(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode {self.filename}. Starting with no alerts.")
                    return []
        return []

    def _save_alerts(self):
        with open(self.filename, 'w') as f:
            json.dump(self.alerts, f, indent=4)

    def add_alert(self, symbol, asset_type, target_price, condition):
        """Adds a new alert."""
        if condition.lower() not in ["above", "below"]:
            print("Invalid condition. Use 'above' or 'below'.")
            return

        alert = {
            "symbol": symbol.upper(),
            "type": asset_type.lower(),
            "target_price": target_price,
            "condition": condition.lower(),
            "triggered": False
        }
        self.alerts.append(alert)
        print(f"Alert added for {symbol}: price {condition} {target_price:.2f}")
        self._save_alerts()

    def remove_alert(self, symbol, asset_type, target_price, condition):
        """Removes a specific alert."""
        initial_count = len(self.alerts)
        self.alerts = [
            a for a in self.alerts
            if not (a["symbol"].upper() == symbol.upper() and
                    a["type"].lower() == asset_type.lower() and
                    a["target_price"] == target_price and
                    a["condition"].lower() == condition.lower())
        ]
        if len(self.alerts) < initial_count:
            print(f"Alert removed for {symbol} ({condition} {target_price:.2f}).")
            self._save_alerts()
        else:
            print(f"Alert not found for {symbol} ({condition} {target_price:.2f}).")

    def check_alerts(self, api_client_instance): # Renamed
        """Checks all active alerts against current prices."""
        print("\n--- Checking Alerts ---")
        triggered_alerts = []
        for alert in self.alerts:
            symbol = alert["symbol"]
            asset_type = alert["type"]
            target_price = alert["target_price"]
            condition = alert["condition"]

            if alert["triggered"]:
                continue

            current_price = None
            if asset_type == "stock":
                data = api_client_instance.get_stock_price(symbol)
                if data:
                    current_price = data['price']
            elif asset_type == "crypto":
                coingecko_id_map = {"BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "DOGE": "dogecoin"}
                coingecko_id = coingecko_id_map.get(symbol.upper(), symbol.lower())
                data = api_client_instance.get_crypto_price(coingecko_id)
                if data:
                    current_price = data['price']

            if current_price is not None:
                alert_triggered = False
                if condition == "above" and current_price >= target_price:
                    alert_triggered = True
                elif condition == "below" and current_price <= target_price:
                    alert_triggered = True

                if alert_triggered:
                    print(f"!!! ALERT !!! {symbol} ({asset_type.capitalize()}) current price ${current_price:.2f} is {condition} target price ${target_price:.2f}!")
                    alert["triggered"] = True
                    triggered_alerts.append(alert)
            else:
                print(f"Could not get current price for {symbol} to check alert.")

        if triggered_alerts:
            self._save_alerts()

        if not triggered_alerts:
            print("No alerts triggered.")
        print("-" * 30)
        return triggered_alerts

    def reset_alert_status(self, symbol=None, asset_type=None, target_price=None, condition=None):
        """Resets the 'triggered' status of alerts. If no args, resets all."""
        if symbol is None and asset_type is None and target_price is None and condition is None:
            for alert in self.alerts:
                alert["triggered"] = False
            print("All alerts reset.")
        else:
            found = False
            for alert in self.alerts:
                match_symbol = symbol is None or alert["symbol"].upper() == symbol.upper()
                match_type = asset_type is None or alert["type"].lower() == asset_type.lower()
                match_price = target_price is None or alert["target_price"] == target_price
                match_condition = condition is None or alert["condition"].lower() == condition.lower()

                if match_symbol and match_type and match_price and match_condition:
                    alert["triggered"] = False
                    print(f"Alert for {alert['symbol']} ({alert['condition']} {alert['target_price']}) reset.")
                    found = True
            if not found:
                print("No matching alert found to reset.")
        self._save_alerts()

    def list_alerts(self):
        """Lists all current alerts."""
        print("\n--- Your Active Alerts ---")
        if not self.alerts:
            print("No alerts set.")
            return

        table = PrettyTable()
        table.field_names = ["Symbol", "Type", "Target Price", "Condition", "Triggered"]

        for alert in self.alerts:
            table.add_row([
                alert["symbol"],
                alert["type"].capitalize(),
                f"${alert['target_price']:.2f}",
                alert["condition"].capitalize(),
                "Yes" if alert["triggered"] else "No"
            ])
        print(table)
        print("-" * 30)

if __name__ == "__main__":
    print("AlertManager class defined.")