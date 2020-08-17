from flask import Flask, render_template, jsonify, redirect, request, make_response, session, g
from api import NEWS_API_KEY, STOCK_API_KEY_1, STOCK_API_KEY_2, STOCK_API_KEY_3
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, SignUpForm
from models import Company, Watchlist, User, connect_db, db
from newsapi import NewsApiClient
from urllib.request import urlopen
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
import requests, random, json, os


CURR_USER_KEY = "curr_user"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///stock_market'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "1234hello1234"
toolbar = DebugToolbarExtension(app)

connect_db(app)

STOCK_API_URL = "https://www.alphavantage.co/query?"
newsapi = NewsApiClient(api_key=NEWS_API_KEY)


##############################################################################
# NEWS API CALL FUNCTIONS
##############################################################################


def get_company_news(name):
    company = get_company_info(name)
    nname, *inc = company["name"].replace(',',' ').split()
    company_news = newsapi.get_everything(q=f'{nname}',
                                          language='en',
                                          )
    temp = company_news["articles"] 
    news_list = []
    for item in temp:
        news = {
            "title" : item["title"],
            "description" : item["description"],
            "url" : item["url"],
            "urlToImage" : item["urlToImage"],
            "publishedAt" : item["publishedAt"]
        };
        news_list.append(news)

    return news_list


##############################################################################
# STOCK DATA API CALL FUNCTIONS
##############################################################################


def get_company_info(name):
    url = (f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={name}&apikey={STOCK_API_KEY_1}")
    response = urlopen(url)
    data = response.read().decode("utf-8")
    info = json.loads(data)
    company_profile = {
        "name" : info["Name"],
        "exchange" : info["Exchange"],
        "industry" : info["Industry"],
        "sector" : info["Sector"],
        "description" : info["Description"]
    }
    return company_profile


def get_stock_data(name):
    stock_price_url = (f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=full&symbol={name}&apikey={STOCK_API_KEY_2}")
    response = urlopen(stock_price_url)
    data = response.read().decode("utf-8")
    stock_data = json.loads(data)
    stock_result = []
    temp_data = stock_data["Time Series (Daily)"]

    for item in temp_data:
        price_data = {
            "date" : item,
            "price" : temp_data[item]["4. close"],
            "volume": temp_data[item]["5. volume"],
        }
        stock_result.append(price_data.copy())

    return stock_result[0:261]


def get_sma_(name):
    sma_price_url = (f"{STOCK_API_URL}function=SMA&symbol={name}&interval=daily&time_period=20&series_type=open&apikey={STOCK_API_KEY_3}")
    response = urlopen(sma_price_url)
    data = response.read().decode("utf-8")
    sma_data = json.loads(data)
    sma_result = []
    temp_data = sma_data["Technical Analysis: SMA"]

    for item in temp_data:
        sma_price = {
            "date" : item,
            "sma" : temp_data[item]["SMA"]
        }
        sma_result.append(sma_price)

    return sma_result[0:261]


@app.route("/api/stock/chart", methods=["POST"])
def send_chart_json_data():
    
    response = request.get_json()
    result = json.dumps(response)
    res = json.loads(result)
    name = res["name"]

    json_response = {}
    json_response["company"] = get_company_info(name)
    json_response["stock"] = get_stock_data(name)
    json_response["sma"] = get_sma_(name)
    json_response["news"] = get_company_news(name)
    
    return make_response(jsonify(json_response),200)

##############################################################################
# USER PAGES 
##############################################################################


@app.before_request
def add_user_to_g():

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):

    session[CURR_USER_KEY] = user.id

def do_logout():

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route("/")
def homepage():

    if not g.user:
        return redirect("/signup")
    else:
        return render_template("users/user_page.html")

@app.route('/signup', methods=["GET", "POST"])
def signup():

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    
    form = SignUpForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                fullname=form.fullname.data,
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError as e:
            return render_template('users/signup.html', form=form)

        do_login(user)

        return render_template("users/user_page.html")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():

    form = LoginForm()
    if g.user:
        return redirect('/')
    else: 
        if form.validate_on_submit():
            try:
                user = User.authenticate(form.username.data,
                                        form.password.data)
                if user:
                    do_login(user)

                    return redirect("/")

            except:
                return redirect("/signup")

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():

    do_logout()

    return redirect("/login")

