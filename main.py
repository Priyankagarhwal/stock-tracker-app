
import time
import os
import sys
import schedule
from asciichartpy import plot as ascii_plot

# --- ADD THESE IMPORTS ---
from api_client import APIClient
from portfolio_manager import PortfolioManager
from alert_manager import AlertManager
# -------------------------

# Global instances
api_client = APIClient()
portfolio_manager = PortfolioManager()
alert_manager = AlertManager()

# ... rest of your main.py code ...
def clear_screen():
    # In Colab, os.system('clear') might not visibly clear the cell output in the same way.
    # It executes, but the notebook UI keeps previous outputs.
    # For a true "fresh screen" feel in Colab, you'd usually clear the cell output programmatically
    # which is not standard Python. For a terminal, this works fine.
    # We'll just print new lines to push old content up.
    print("\n" * 50) # Simulate clear by printing many newlines
    # Or simply: pass # if you don't want to attempt clearing

def display_menu():
    clear_screen()
    print("--- Stock/Crypto Tracker ---")
    print("1. View Current Prices")
    print("2. Manage Portfolio")
    print("3. Manage Alerts")
    print("4. View Historical Data (ASCII Chart)")
    print("5. Start Real-time Monitoring (and alerts)")
    print("6. Exit")
    print("----------------------------")

def view_current_prices():
    print("\n--- Current Prices ---")
    symbol = input("Enter stock symbol (e.g., AAPL) or crypto ID (e.g., BTC): ").upper()
    asset_type = input("Is this 'stock' or 'crypto'? ").lower()

    if asset_type == 'stock':
        data = api_client.get_stock_price(symbol)
        if data:
            print(f"\n{symbol}:")
            print(f"  Price: ${data['price']:.2f}")
            print(f"  Change: {data['change']:.2f}")
            print(f"  Change (%): {data['change_percent']}")
    elif asset_type == 'crypto':
        coingecko_id_map = {"BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "DOGE": "dogecoin", "SOL": "solana"} # Extend this!
        coingecko_id = coingecko_id_map.get(symbol, symbol.lower())
        data = api_client.get_crypto_price(coingecko_id)
        if data:
            print(f"\n{symbol} ({coingecko_id.capitalize()}):")
            print(f"  Price: ${data['price']:.2f}")
    else:
        print("Invalid asset type.")
    input("\nPress Enter to continue...")

def manage_portfolio():
    while True:
        clear_screen()
        print("\n--- Portfolio Management ---")
        print("1. View My Portfolio")
        print("2. Add Holding")
        print("3. Remove Holding")
        print("4. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            portfolio_manager.display_portfolio_summary(api_client)
            input("\nPress Enter to continue...")
        elif choice == '2':
            symbol = input("Enter stock symbol (e.g., AAPL) or crypto ID (e.g., BTC): ").upper()
            try:
                quantity = float(input("Enter quantity: "))
                if quantity <= 0:
                    raise ValueError("Quantity must be positive.")
            except ValueError as e:
                print(f"Invalid quantity: {e}")
                input("Press Enter to continue...")
                continue
            asset_type = input("Is this 'stock' or 'crypto'?: ").lower()
            if asset_type not in ['stock', 'crypto']:
                print("Invalid asset type. Must be 'stock' or 'crypto'.")
                input("Press Enter to continue...")
                continue
            portfolio_manager.add_holding(symbol, quantity, asset_type)
            input("\nPress Enter to continue...")
        elif choice == '3':
            symbol = input("Enter stock symbol (e.g., AAPL) or crypto ID (e.g., BTC) to remove: ").upper()
            asset_type = input("Is this 'stock' or 'crypto'?: ").lower()
            if asset_type not in ['stock', 'crypto']:
                print("Invalid asset type. Must be 'stock' or 'crypto'.")
                input("Press Enter to continue...")
                continue
            portfolio_manager.remove_holding(symbol, asset_type)
            input("\nPress Enter to continue...")
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

def manage_alerts():
    while True:
        clear_screen()
        print("\n--- Alert Management ---")
        print("1. View All Alerts")
        print("2. Add New Alert")
        print("3. Remove Alert")
        print("4. Reset Triggered Status of Alerts")
        print("5. Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            alert_manager.list_alerts()
            input("\nPress Enter to continue...")
        elif choice == '2':
            symbol = input("Enter stock symbol (e.g., AAPL) or crypto ID (e.g., BTC): ").upper()
            asset_type = input("Is this 'stock' or 'crypto'?: ").lower()
            if asset_type not in ['stock', 'crypto']:
                print("Invalid asset type. Must be 'stock' or 'crypto'.")
                input("Press Enter to continue...")
                continue
            try:
                target_price = float(input("Enter target price: "))
                if target_price <= 0:
                    raise ValueError("Target price must be positive.")
            except ValueError as e:
                print(f"Invalid price: {e}")
                input("Press Enter to continue...")
                continue
            condition = input("Trigger 'above' or 'below' this price?: ").lower()
            if condition not in ['above', 'below']:
                print("Invalid condition. Must be 'above' or 'below'.")
                input("Press Enter to continue...")
                continue
            alert_manager.add_alert(symbol, asset_type, target_price, condition)
            input("\nPress Enter to continue...")
        elif choice == '3':
            symbol = input("Enter stock symbol (e.g., AAPL) or crypto ID (e.g., BTC) to remove alert for: ").upper()
            asset_type = input("Is this 'stock' or 'crypto'?: ").lower()
            try:
                target_price = float(input("Enter target price for the alert to remove: "))
            except ValueError:
                print("Invalid target price.")
                input("Press Enter to continue...")
                continue
            condition = input("Enter condition ('above' or 'below') for the alert to remove: ").lower()
            alert_manager.remove_alert(symbol, asset_type, target_price, condition)
            input("\nPress Enter to continue...")
        elif choice == '4':
            confirm = input("Reset ALL triggered alerts? (yes/no): ").lower()
            if confirm == 'yes':
                alert_manager.reset_alert_status()
            else:
                print("No alerts reset.")
            input("\nPress Enter to continue...")
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

def view_historical_data():
    clear_screen()
    print("\n--- Historical Data (ASCII Chart) ---")
    symbol = input("Enter stock symbol (e.g., AAPL): ").upper()

    data = api_client.get_historical_stock_data(symbol, interval="daily", outputsize="compact")
    if data:
        dates = sorted(data.keys())
        # Filter out dates where closing price might be missing or invalid
        closing_prices = []
        valid_dates = []
        for d in dates:
            try:
                price = float(data[d]['4. close'])
                closing_prices.append(price)
                valid_dates.append(d)
            except (ValueError, KeyError):
                continue # Skip invalid entries

        if closing_prices:
            print(f"\nDaily Closing Prices for {symbol} (Last {len(closing_prices)} days):")
            # Use ascii_plot directly as it's imported
            print(ascii_plot(closing_prices, {'height': 10}))
            if valid_dates: # Ensure we have valid dates to show
                print(f"Oldest: {valid_dates[0]} Price: ${closing_prices[0]:.2f}")
                print(f"Newest: {valid_dates[-1]} Price: ${closing_prices[-1]:.2f}")
        else:
            print(f"No valid historical data found for {symbol} to plot.")
    else:
        print(f"Could not fetch historical data for {symbol}.")
    input("\nPress Enter to continue...")

def start_realtime_monitoring():
    clear_screen()
    print("--- Real-time Monitoring ---")
    print("Portfolio summary will refresh every 1 minute.")
    print("Alerts will be checked every 30 seconds.")
    print("To stop monitoring: Click the 'Stop' button (square icon) next to this cell's run button.")

    # Clear any previous schedule jobs before setting new ones
    schedule.clear()

    # Schedule tasks
    schedule.every(1).minutes.do(lambda: portfolio_manager.display_portfolio_summary(api_client))
    schedule.every(30).seconds.do(lambda: alert_manager.check_alerts(api_client))

    # Initial display
    portfolio_manager.display_portfolio_summary(api_client)
    alert_manager.list_alerts()

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        # This block might not be easily triggered by Colab's stop button
        print("\nMonitoring stopped by KeyboardInterrupt.")
    except Exception as e:
        print(f"An error occurred during monitoring: {e}")
    finally:
        print("Returning to main menu...")
        # In Colab, the cell execution will stop, so 'finally' might not run before the next cell
        # is manually executed.
        schedule.clear() # Clean up schedule jobs

def main():
    while True:
        display_menu()
        choice = input("Enter your choice: ")
        if choice == '1':
            view_current_prices()
        elif choice == '2':
            manage_portfolio()
        elif choice == '3':
            manage_alerts()
        elif choice == '4':
            view_historical_data()
        elif choice == '5':
            start_realtime_monitoring()
            # After monitoring stops (by manual interruption in Colab), the loop continues
            # to show the menu again.
        elif choice == '6':
            print("Exiting. Goodbye!")
            sys.exit() # Use sys.exit() to stop the Colab runtime
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)

# This is the entry point for running the whole application
# when you execute this cell.
print("Main application logic defined. Running main()...")
main()