from flask import Flask,render_template,session,redirect,url_for
from BSM import bsm
from SCC import scc
from MC import mc
from PV import pv
from News import News
from AboutUs import AboutUs
from Ticker import ticker_bp
from Cards import stocks_bp
from form import form
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = "192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf"

# Register blueprints
app.register_blueprint(bsm, url_prefix='/BSM')
app.register_blueprint(scc, url_prefix='/SCC')
app.register_blueprint(mc, url_prefix='/MC')
app.register_blueprint(pv, url_prefix='/PV')
app.register_blueprint(News,url_prefix='/NEWS')
app.register_blueprint(AboutUs,url_prefix="/ABOUTUS")
app.register_blueprint(ticker_bp)
app.register_blueprint(stocks_bp,url_prefix='/stocks')
app.register_blueprint(form,url_prefix='/form/')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('form.login'))
    return render_template('form.html')  # Create this template

if __name__ == '__main__':
    app.run(debug=True)
