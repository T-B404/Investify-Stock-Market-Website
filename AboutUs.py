from flask import Flask,render_template,Blueprint

AboutUs=Blueprint('AboutUs',__name__)

@AboutUs.route('/')
def about():
    return render_template('AboutUs.html')