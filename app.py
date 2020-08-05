from flask import Flask, render_template, jsonify, request, make_response, session, g
from api import NEWS_API_KEY, STOCK_API_KEY
from newsapi import NewsApiClient
import requests, random, json

CURR_USER_KEY = "curr_user"
app = Flask(__name__)

BASE_API_URL = "https://financialmodelingprep.com/api/v3/"

##############################################################################
# API calls seperated from view functinos

# def get_company_profile(ticker):
#     company_profile = requests.get(
#         f"{BASE_API_URL}/profile/{ticker}?apikey={API_KEY}"
#         )
#     company_info = company_profile.json()
#     info = json.dumps(company_info)
#     return info

# def get_company_stock(ticker):

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def get_financial_news(ticker):
    top_headlines = newsapi.get_top_headlines(
            q='apple',
            language='en',
            country='us'
            )
    print(top_headlines)
    return top_headlines


##############################################################################
# Homepage


@app.route("/")
def homepage():
    return render_template("homepage.html")


##############################################################################
# Company Profile

@app.route("/api/search/company/news", methods=["POST"])
def search_ticker():
    req = request.get_json()
    company_name = req.get("company")
    top_headlines = newsapi.get_top_headlines(
            q='apple',
            language='en',
            country='us'
            )
    return make_response(jsonify(top_headlines)), 200
    
##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

