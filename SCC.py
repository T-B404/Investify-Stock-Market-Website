import datetime as dt
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import yfinance as yt
from flask import Flask,render_template,request,jsonify,Blueprint
from plotly.utils import PlotlyJSONEncoder
import json

scc = Blueprint('scc',__name__)
#app = Flask(__name__)
# Defining timeframe of chart
def fetch_data(ticker,sdate,edate):
    # ticker=input("Enter the stock ticker symbol (eg., AAPL): ")
    # startDate=input("Enter start date (YYYY-MM-DD): ")
    # endDate=input("Enter end date (YYYY-MM-DD): ")
    data=request.get_json()
    ticker=data.get('ticker')
    startDate=data.get('sdate')
    endDate=data.get('edate')

    start = dt.datetime.strptime(startDate,"%Y-%m-%d")
    end = dt.datetime.strptime(endDate,"%Y-%m-%d")
    data = yt.download(ticker,start,end)
    #print(data)

    # # Restructuring data

    data.columns=[' '.join(col).strip() for col in data.columns.values]
    data.rename(columns={
        'Open '+ticker:'Open',
        'High '+ticker:'High',
        'Low '+ticker:'Low',
        'Close '+ticker:'Close',
        'Date '+ticker:'Date'},
        inplace=True)
    data = data [['Open', 'High', 'Low', 'Close']]

    data.reset_index(inplace=True)
    data['Date'] = pd.to_datetime(data['Date'])
    # print(data.isna().sum())
    data = data.dropna()
    return data
    # print(f"Data for {ticker} from {start} to {end}")
    # print(data.head())

def generate_candlestick_chart(df):
    df['Date'] = df['Date'].dt.strftime('%b %d, %Y')  # Convert dates to 'Jan 28, 2025' format

    fig = go.Figure(data=[go.Candlestick(
        x=df['Date'],  # Use formatted date
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing=dict(line=dict(color='green', width=2)),
        decreasing=dict(line=dict(color='red', width=2))
    )])

    layout = go.Layout(
        title=f"Candlestick Chart",
        title_x=0.5,
        title_xanchor='center',
        xaxis_title='Date',
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False,
        template='plotly_white',
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False,
            tickangle=-25,  # Tilt labels for better visibility
            automargin=True
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False
        )
    )

    fig.update_layout(layout)

    graph_data = fig.to_dict()

    # Convert NumPy arrays to lists
    for key in ['x', 'open', 'high', 'low', 'close']:
        graph_data['data'][0][key] = graph_data['data'][0][key].tolist()

    return graph_data


#@app.route("/SCC/api/get_chart_data",methods=['POST'])
@scc.route("/api/get_chart_data",methods=['POST'])
def get_chart_data():
    data=request.get_json()
    ticker=data['ticker']
    sdate=data['sdate']
    edate=data['edate']

    df=fetch_data(ticker,sdate,edate)
    chart_data=generate_candlestick_chart(df)
    df_dict=df.to_dict(orient='records')
    return jsonify({
        'chart':chart_data,
        'stock_data':df_dict
    })

# @app.route("/")
@scc.route("/")
def index():
    return render_template('SCCindex.html')

# if __name__=='__main__':
#     app.run(debug=True)




