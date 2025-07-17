from flask import Flask,render_template,request,jsonify,Blueprint
from scipy.stats import norm
import math
from sympy import symbols,log,exp,sqrt,latex
from sympy.stats import Normal,cdf
bsm=Blueprint('bsm',__name__)

#app = Flask(__name__)

#@app.route("/")
@bsm.route('/')
def index():
    return render_template('BSMindex.html')

#@app.route("/calculate",methods=['POST'])
@bsm.route("/calculate",methods=['POST'])
def calculate():
    try:
        data = request.json
        S=float(data.get('S',0))
        K=float(data.get('K',0))
        T=float(data.get('T',0))
        r=float(data.get('r',0))
        vol=float(data.get('vol',0))

        if S<=0 or K<=0 or T<= 0 or vol<=0:
            return jsonify({'error':'All inputs must be positive.'})
        
        result=cal_optionprices(S,K,T,r,vol)
        steps_latex=solve_black_scholes(S,K,T,r,vol)

        return jsonify({
            'result':result,
            'steps':f"{steps_latex}"})
    except Exception as e:
        return jsonify({'error': str(e)})

def cal_optionprices(S,K,T,r,vol):
    d1 = (math.log(S/K) + (r + 0.5*vol**2)*T) / (vol * math.sqrt(T))

    d2 = d1 - (vol * math.sqrt(T))

    C = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)

    P = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return {
        'd1':round(d1,4),
        'd2':round(d2,4),
        'call-option':round(C,2),
        'put-option':round(P,2)
    }

def solve_black_scholes(S,K,T,r,vol):

    S,K,T,r,vol = symbols('S K T r vol')
    d1 = (log(S/K)+(r+0.5*vol**2)*T)/(vol*sqrt(T))
    d2=d1-vol*sqrt(T)
    
    call_price = S*cdf(Normal('X',0,1),d1)-K*exp(-r*T)*cdf(Normal('X',0,1),d2)
    put_price = K*exp(-r*T)*cdf(Normal('X',0,1),-d2)-S*cdf(Normal('X',0,1),-d1)
    
    d1_latex = latex(d1)
    d2_latex = latex(d2)
    call_price_latex = latex(call_price)
    put_price_latex = latex(put_price)


    steps_latex=f"""
    $d_1 = {d1_latex}$ \\\\
    $d_2 = {d2_latex}$ \\\\
    $(C) = {call_price_latex}$ \\\\
    $(P) = {put_price_latex}$
    """
    return steps_latex

# if __name__=='__main__':
#     app.run(debug=True)
    