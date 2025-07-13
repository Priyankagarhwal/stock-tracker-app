# Stock Tracker Web Application

A comprehensive web application for tracking stocks and cryptocurrencies, managing your portfolio, and setting price alerts.

## Features

- **Real-time Price Tracking**: Get current prices for stocks and cryptocurrencies
- **Portfolio Management**: Track your investments and monitor their performance
- **Price Alerts**: Set alerts for price movements and get notified
- **Historical Data**: View historical price data with interactive charts
- **Dashboard**: Get a quick overview of your portfolio and market trends
- **Responsive Design**: Works on desktop and mobile devices

## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Data Visualization**: Chart.js
- **APIs**: Alpha Vantage (stocks), CoinGecko (cryptocurrencies)
- **Data Storage**: JSON (local storage)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/stock-tracker-app.git
   cd stock-tracker-app
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy the `.env.example` file to a new file named `.env`:
     ```
     cp .env.example .env  # On Windows: copy .env.example .env
     ```
   - Get your Alpha Vantage API key by signing up at [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
   - Edit the `.env` file and replace `your_api_key_here` with your actual API key:
     ```
     ALPHA_VANTAGE_API_KEY=your_actual_api_key
     ```
   - **IMPORTANT**: Never commit your `.env` file to version control. It's already in `.gitignore` to prevent accidental commits.

5. Run the application:
   ```
   python app.py
   ```

6. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
stock_tracker_app/
├── app.py                  # Flask application entry point
├── api_client.py           # API client for external services
├── portfolio_manager.py    # Portfolio management functionality
├── alert_manager.py        # Alert management functionality
├── static/                 # Static files
│   ├── css/                # CSS stylesheets
│   └── js/                 # JavaScript files
├── templates/              # HTML templates
│   ├── base.html           # Base template with common elements
│   ├── index.html          # Dashboard page
│   ├── portfolio.html      # Portfolio management page
│   ├── alerts.html         # Alert management page
│   ├── prices.html         # Price lookup page
│   └── historical.html     # Historical data visualization page
├── .env.example            # Example environment variables template
├── .env                    # Environment variables (not in version control)
└── requirements.txt        # Python dependencies
```

## API Usage

This application uses the following APIs:

- **Alpha Vantage**: For stock price data
  - Sign up for a free API key at [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
  
- **CoinGecko**: For cryptocurrency price data
  - No API key required for basic usage

## Future Enhancements

- User authentication and multiple portfolios
- Email notifications for triggered alerts
- Advanced technical analysis indicators
- Portfolio performance metrics and reports
- Integration with trading platforms
- Mobile app version

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Alpha Vantage](https://www.alphavantage.co/) for stock market data
- [CoinGecko](https://www.coingecko.com/) for cryptocurrency data
- [Bootstrap](https://getbootstrap.com/) for the UI framework
- [Chart.js](https://www.chartjs.org/) for data visualization