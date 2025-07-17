import datetime as dt
import plotly.graph_objects as go
import pandas_datareader as web
import yfinance as yf
import sqlite3
from flask import Flask, request, jsonify, render_template,Blueprint
import json
from plotly.utils import PlotlyJSONEncoder
import pandas as pd

pv=Blueprint('pv',__name__)

#app=Flask(__name__)
# Connecting SQLite Database
def connection_db():
    conn=sqlite3.connect('portfolio.db',check_same_thread=False) # Connection object
    cursor=conn.cursor() # Cursor for executing queries and interacting with database
    cursor.execute("""CREATE table if not exists portfolio (
                    id INTEGER PRIMARY KEY,
                    ticker TEXT,
                    amount INTEGER,
                    purchase_price REAL,
                    added_on TEXT,
                    period TEXT)""")
    conn.commit() # Saving changes to database
    return conn,cursor

conn,cursor=connection_db()

# Adding stock to portfolio
#@app.route("/api/portfolio",methods=['POST'])
@pv.route("/api/portfolio",methods=['POST'])
def add_stock():
    data = request.json
    ticker = data.get('ticker')
    amount = data.get('amount')
    period = data.get('period', '1d')

    try:
        # Fetch data with the CORRECT period
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period=period)
        
        # Validate data availability
        if stock_data.empty or 'Close' not in stock_data.columns:
            return jsonify({"error": f"No price data for {ticker} (period={period})"}), 400
        
        current_price = stock_data['Close'].iloc[-1]
    except Exception as e:
        return jsonify({"error": f"Failed to fetch data: {str(e)}"}), 500
    cursor.execute('''
        INSERT INTO portfolio (ticker, amount, purchase_price, added_on, period)
        VALUES (?, ?, ?, ?, ?)
    ''', (ticker, amount, current_price, dt.datetime.now(), period))
    conn.commit()

    return jsonify({"message": "Stock added successfully!"})


# Retriving data from database
#@app.route("/api/portfolio",methods=['GET'])
@pv.route("/api/portfolio",methods=['GET'])
def get_portfolio():
    cursor.execute('SELECT ticker , amount, purchase_price,period FROM portfolio')
    portfolio=cursor.fetchall()

    result=[]
    for ticker,amount,purchase_price,period in portfolio:
        current_price = get_current_price(ticker,period)
        profit_or_loss = (current_price-purchase_price)*amount

        result.append({
            "ticker": ticker,
            "amount": amount,
            "purchase_price": purchase_price,
            "current_price": current_price,
            "profit_loss": profit_or_loss
        })
    return jsonify(result)


def get_current_price(ticker,period='1d'):
    stock_data = yf.download(ticker, period=period)
    
    if stock_data.empty or 'Close' not in stock_data.columns:
        return None  # Handle the case where data is missing
    
    last_close = stock_data['Close'].iloc[-1]
    
    if isinstance(last_close, pd.Series):
        last_close = last_close.iloc[0]  # Ensure a single value
    
    return float(last_close)

# Updating the database
# @app.route("/api/portfolio/<ticker>",methods=['PUT'])
@pv.route("/api/portfolio/<ticker>",methods=['PUT'])
def update_portfolio(ticker):
    data = request.json
    amount = data.get('amount')

    if amount==0:
        cursor.execute('DELETE FROM portfolio WHERE ticker=?',(ticker,))
        message = f'Stock {ticker} was removed from your portfolio.'
    else:
        cursor.execute('UPDATE portfolio SET amount=? WHERE ticker=?',(amount,ticker))
        message=f"Stock {ticker} updated to {amount} shares."
    conn.commit()
    return jsonify({'message':message})

#@app.route("/api/portfolio-chart",methods=['GET'])
@pv.route("/api/portfolio-chart",methods=['GET'])
def plotting_chart():
    connection = sqlite3.connect('portfolio.db')
    cursor=connection.cursor()
    cursor.execute("SELECT ticker,amount,purchase_price,period FROM portfolio")
    portfolio=cursor.fetchall()

    if not portfolio:
        return jsonify({'error':"Portfolio is empty"}),400
    
    tickers=[entry[0] for entry in portfolio]
    amounts=[entry[1] for entry in portfolio]
    periods = [entry[3] for entry in portfolio]

    total=[]
    for ticker,amount,period in zip(tickers,amounts,periods):
        current_price = get_current_price(ticker,period)
        total.append(current_price*amount)

    fig = go.Figure(data=[go.Pie(labels=tickers,values=total,hole=0.5)])

    fig.update_layout(
        title='Portfolio Overview',
    )
    graph_json = json.dumps(fig,cls=PlotlyJSONEncoder)
    return graph_json
    # fig.show()

# @app.route('/')
@pv.route('/')
def index():
    return render_template("PVindex.html")

# if __name__=='__main__':
#     app.run(debug=True)

