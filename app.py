from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from dotenv import load_dotenv
from api_client import APIClient
from portfolio_manager import PortfolioManager
from alert_manager import AlertManager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages

# Initialize our classes
api_client = APIClient()
portfolio_manager = PortfolioManager()
alert_manager = AlertManager()

@app.route('/')
def index():
    """Home page with dashboard overview"""
    return render_template('index.html')

@app.route('/prices')
def prices():
    """Page for viewing current prices"""
    return render_template('prices.html')

@app.route('/get_price', methods=['POST'])
def get_price():
    """API endpoint to get current price data"""
    symbol = request.form.get('symbol', '').upper()
    asset_type = request.form.get('asset_type', '').lower()
    
    if asset_type == 'stock':
        data = api_client.get_stock_price(symbol)
        if data:
            return jsonify({
                'success': True,
                'symbol': symbol,
                'price': data['price'],
                'change': data['change'],
                'change_percent': data['change_percent']
            })
    elif asset_type == 'crypto':
        coingecko_id_map = {"BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "DOGE": "dogecoin", "SOL": "solana"}
        coingecko_id = coingecko_id_map.get(symbol, symbol.lower())
        data = api_client.get_crypto_price(coingecko_id)
        if data:
            return jsonify({
                'success': True,
                'symbol': symbol,
                'price': data['price']
            })
    
    return jsonify({'success': False, 'message': f'Could not fetch data for {symbol}'})

@app.route('/portfolio')
def portfolio():
    """Portfolio management page"""
    holdings = portfolio_manager.get_all_holdings()
    return render_template('portfolio.html', holdings=holdings)

@app.route('/portfolio/add', methods=['POST'])
def add_holding():
    """Add a holding to the portfolio"""
    symbol = request.form.get('symbol', '').upper()
    try:
        quantity = float(request.form.get('quantity', 0))
        if quantity <= 0:
            flash('Quantity must be positive', 'danger')
            return redirect(url_for('portfolio'))
    except ValueError:
        flash('Invalid quantity', 'danger')
        return redirect(url_for('portfolio'))
    
    asset_type = request.form.get('asset_type', '').lower()
    if asset_type not in ['stock', 'crypto']:
        flash('Invalid asset type', 'danger')
        return redirect(url_for('portfolio'))
    
    portfolio_manager.add_holding(symbol, quantity, asset_type)
    flash(f'Added {quantity} of {symbol} to portfolio', 'success')
    return redirect(url_for('portfolio'))

@app.route('/portfolio/remove', methods=['POST'])
def remove_holding():
    """Remove a holding from the portfolio"""
    symbol = request.form.get('symbol', '').upper()
    asset_type = request.form.get('asset_type', '').lower()
    
    portfolio_manager.remove_holding(symbol, asset_type)
    flash(f'Removed {symbol} from portfolio', 'success')
    return redirect(url_for('portfolio'))

@app.route('/portfolio/summary')
def portfolio_summary():
    """API endpoint to get portfolio summary data"""
    holdings = portfolio_manager.get_all_holdings()
    summary_data = []
    total_value = 0
    
    for holding in holdings:
        symbol = holding["symbol"]
        quantity = holding["quantity"]
        asset_type = holding["type"]
        current_price = None
        daily_change_percent = "N/A"
        
        if asset_type == "stock":
            data = api_client.get_stock_price(symbol)
            if data:
                current_price = data['price']
                daily_change_percent = data['change_percent']
        elif asset_type == "crypto":
            coingecko_id_map = {"BTC": "bitcoin", "ETH": "ethereum", "XRP": "ripple", "DOGE": "dogecoin"}
            coingecko_id = coingecko_id_map.get(symbol.upper(), symbol.lower())
            data = api_client.get_crypto_price(coingecko_id)
            if data:
                current_price = data['price']
        
        if current_price is not None:
            value = current_price * quantity
            total_value += value
            summary_data.append({
                'symbol': symbol,
                'type': asset_type.capitalize(),
                'quantity': quantity,
                'price': current_price,
                'value': value,
                'change_percent': daily_change_percent
            })
        else:
            summary_data.append({
                'symbol': symbol,
                'type': asset_type.capitalize(),
                'quantity': quantity,
                'price': 'N/A',
                'value': 'N/A',
                'change_percent': 'N/A'
            })
    
    return jsonify({
        'holdings': summary_data,
        'total_value': total_value
    })

@app.route('/alerts')
def alerts():
    """Alerts management page"""
    all_alerts = alert_manager.alerts
    return render_template('alerts.html', alerts=all_alerts)

@app.route('/alerts/add', methods=['POST'])
def add_alert():
    """Add a new price alert"""
    symbol = request.form.get('symbol', '').upper()
    asset_type = request.form.get('asset_type', '').lower()
    
    try:
        target_price = float(request.form.get('target_price', 0))
        if target_price <= 0:
            flash('Target price must be positive', 'danger')
            return redirect(url_for('alerts'))
    except ValueError:
        flash('Invalid target price', 'danger')
        return redirect(url_for('alerts'))
    
    condition = request.form.get('condition', '').lower()
    if condition not in ['above', 'below']:
        flash('Invalid condition', 'danger')
        return redirect(url_for('alerts'))
    
    alert_manager.add_alert(symbol, asset_type, target_price, condition)
    flash(f'Alert added for {symbol}', 'success')
    return redirect(url_for('alerts'))

@app.route('/alerts/remove', methods=['POST'])
def remove_alert():
    """Remove a price alert"""
    symbol = request.form.get('symbol', '').upper()
    asset_type = request.form.get('asset_type', '').lower()
    
    try:
        target_price = float(request.form.get('target_price', 0))
    except ValueError:
        flash('Invalid target price', 'danger')
        return redirect(url_for('alerts'))
    
    condition = request.form.get('condition', '').lower()
    
    alert_manager.remove_alert(symbol, asset_type, target_price, condition)
    flash(f'Alert removed for {symbol}', 'success')
    return redirect(url_for('alerts'))

@app.route('/alerts/reset', methods=['POST'])
def reset_alerts():
    """Reset all triggered alerts"""
    alert_manager.reset_alert_status()
    flash('All alerts have been reset', 'success')
    return redirect(url_for('alerts'))

@app.route('/alerts/check')
def check_alerts():
    """API endpoint to check alerts"""
    triggered = alert_manager.check_alerts(api_client)
    return jsonify({
        'triggered_count': len(triggered),
        'triggered_alerts': triggered
    })

@app.route('/historical')
def historical():
    """Historical data visualization page"""
    return render_template('historical.html')

@app.route('/get_historical_data', methods=['POST'])
def get_historical_data():
    """API endpoint to get historical price data"""
    symbol = request.form.get('symbol', '').upper()
    interval = request.form.get('interval', 'daily')
    
    data = api_client.get_historical_stock_data(symbol, interval, "compact")
    if not data:
        return jsonify({'success': False, 'message': f'Could not fetch historical data for {symbol}'})
    
    # Process data for chart
    dates = sorted(data.keys())
    chart_data = []
    
    for date in dates:
        try:
            price = float(data[date]['4. close'])
            chart_data.append({
                'date': date,
                'price': price
            })
        except (ValueError, KeyError):
            continue
    
    return jsonify({
        'success': True,
        'symbol': symbol,
        'data': chart_data
    })

if __name__ == '__main__':
    app.run(debug=True)