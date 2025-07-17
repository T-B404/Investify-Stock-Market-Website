from flask import Flask, render_template, request, jsonify, Blueprint
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import random

mc=Blueprint('mc',__name__)
#app=Flask(__name__)
#@app.route('/')
@mc.route('/')
def index():
    return render_template('MCindex.html')

#@app.route('/simulate', methods=['POST'])
@mc.route('/simulate', methods=['POST'])
def stimulate():
    try:
        data = request.get_json()

        if 'company_name' not in data or 'start_date' not in data or 'end_date' not in data:
            return jsonify({"error": "Missing required fields (company_name, start_date, end_date)."}), 400

        company = data['company_name']
        sdate = data['start_date']
        edate = data['end_date']

        try:
            datetime.strptime(sdate, '%Y-%m-%d')
            datetime.strptime(edate, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

        fig = create_stiplot(company, sdate, edate)

        if fig:
            return jsonify(fig) 
        else:
            return jsonify({'error':'Failed to generate plot'}), 500
    
    except Exception as e:
        mc.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def create_stiplot(company, sdate, edate):
    data = yf.download(company, start=sdate, end=edate)
    if 'Close' in data.columns:
        close_prices = data['Close']
    else:
        print("Error: 'Close' column not found in the data.")
        return None 

    returns = np.log(1 + close_prices.pct_change()).dropna()
    mu, sigma = returns.mean(), returns.std()
    initial_price = close_prices.iloc[-1]

    if isinstance(initial_price, pd.Series):
        initial_price = initial_price.item()

    stimulations = []
    for _ in range(100):  # 100 simulations
        sims_returns = np.random.normal(mu, sigma, 252) 
        stimulated_prices = initial_price * (sims_returns + 1).cumprod()
        stimulations.append(stimulated_prices)

    fig = go.Figure()

    colors=['red','blue','green','purple','orange','pink','brown','cyan','magenta','lime']
    for sim in stimulations:
        fig.add_trace(go.Scatter(
            x=np.arange(len(sim)).tolist(),  
            y=sim.tolist(), 
            mode='lines', 
            line=dict(color=random.choice(colors),width=1)
        ))

    fig.add_trace(go.Scatter(
        x=[0, 252], 
        y=[initial_price, initial_price], 
        mode='lines', 
        line=dict(color='black', dash='dash')
    ))

    fig.update_layout(
        title=f'{company} Monte Carlo Simulation',
        xaxis_title='Days',
        yaxis_title='Price',
        template='plotly_white',
    )
    return fig.to_dict() 

# if __name__=='__main__':
#     app.run(debug=True)

