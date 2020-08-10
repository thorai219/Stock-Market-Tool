from flask import Flask, render_template, jsonify, request, make_response, session, g
from api import NEWS_API_KEY, STOCK_API_KEY
from newsapi import NewsApiClient
from urllib.request import urlopen
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import requests, random, json

CURR_USER_KEY = "curr_user"
app = Flask(__name__)

STOCK_URL = "https://financialmodelingprep.com/api/v3"
newsapi = NewsApiClient(api_key=NEWS_API_KEY)


##############################################################################
# API calls seperated from view functions

# def get_company_info(name):

#     company_news = newsapi.get_top_headlines(
#                     q=f'{name}',
#                     category='business',
#                     language='en',
#                     country='us'
#                     )
#     result = json.dumps(company_news)
#     res = json.loads(result)
#     news = {
#         "title" : res["articles"][0]["title"],
#         "description" : res["articles"][0]["description"],
#         "url" : res["articles"][0]["url"],
#         "urlToImage" : res["articles"][0]["urlToImage"],
#         "publishedAt" : res["articles"][0]["publishedAt"]
#     }
#     return news

# def populate_homepage():

#     top_headlines = newsapi.get_top_headlines(country='us',category='business')
#     result = json.dumps(top_headlines)
#     data = json.loads(result)
#     news = []
#     for res in data["articles"]:
#         article = {
#         "title" : res["title"],
#         "description" : res["description"],
#         "url" : res["url"],
#         "urlToImage" : res["urlToImage"],
#         "publishedAt" : res["publishedAt"]
#         }
#         news.append(article.copy())
    # return news


##############################################################################
# Stock api call

def get_jsonparsed_data(url):

    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)




##############################################################################
# Homepage 
@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/api/stock/chart", methods=["POST"])
def six_months_chart():

    response = request.get_json()
    result = json.dumps(response)
    res = json.loads(result)
    name = res["name"]

    date_today = datetime.date(datetime.now())
    six_months = date.today() + relativedelta(months=-6)

    url = (
    f"{STOCK_URL}/historical-price-full/{name}?from={six_months}&to={date_today}&apikey={STOCK_API_KEY}"   
    )
    
    data = get_jsonparsed_data(url)
    print(jsonify(data))
    result = []

    for item in data["historical"]:
        price_data = {
            "date" : item["date"],
            "price" : item["close"],
        }
        result.insert(0, price_data.copy())
    
    return make_response(jsonify(result),200)

##############################################################################
# Company Profile

# @app.route("/api/search/company/news", methods=["POST"])
# def search_ticker():

#     response = request.get_json()
#     result = json.dumps(response)
#     res = json.loads(result)
#     name = res["name"]

#     return get_company_info(name)
    
##############################################################################
# User signup/login/logout

# @app.before_request
# def add_user_to_g():
#     """If we're logged in, add curr user to Flask global."""
#     if CURR_USER_KEY in session:
#         g.user = User.query.get(session[CURR_USER_KEY])
#     else:
#         g.user = None

# def do_login(user):
#     """Log in user."""
#     session[CURR_USER_KEY] = user.id

# def do_logout():
#     """Logout user."""
#     if CURR_USER_KEY in session:
#         del session[CURR_USER_KEY]

