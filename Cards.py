from flask import Blueprint, jsonify
import yfinance as yf

stocks_bp = Blueprint('stocks', __name__)

LOGOS = {
    'AAPL': '/static/apple.png',
    'GOOGL': '/static/google.png',
    'AMZN': '/static/amazon.png',
    'TSLA': '/static/tesla.png',
    'MSFT': '/static/microsoft.png',
    'NFLX': '/static/netflix.webp'
}

SYMBOLS = ['AAPL', 'GOOGL', 'AMZN', 'TSLA', 'MSFT', 'NFLX']

def fetch_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period='1d')

        if data.empty:
            return {'symbol': symbol, 'price': None, 'error': 'No data available'}

        price = round(data['Close'].iloc[-1], 2)
        return {'symbol': symbol, 'price': price, 'logo': LOGOS.get(symbol, '/static/default.png')}
    
    except Exception as e:
        return {'symbol': symbol, 'price': None, 'error': str(e)}

@stocks_bp.route('/get_stocks')
def get_stocks():
    stock_data = [fetch_stock_price(symbol) for symbol in SYMBOLS]
    return jsonify(stock_data)
