import os
import requests
from flask import Flask,render_template,Blueprint

#app=Flask(__name__)
News=Blueprint('News',__name__)
NEWS_API_KEY=os.getenv("NEWS_API_KEY",'766f6033e0734a81866a20f9ae7c9fb3')

@News.route('/')
def news():
    url = f"https://newsapi.org/v2/everything?q=stock%20market&apiKey={NEWS_API_KEY}"

    response = requests.get(url)

    if response.status_code == 200:
        news_data=response.json()
        articles = news_data.get('articles',[])
        articles=[
            article for article in articles
            if article.get('title') and article.get('url') and article.get('description') and article.get('urlToImage')
        ]
    else:
        articles = []

    return render_template('news.html',articles=articles)

# if __name__=='__main__':
#     app.run(debug=True)
