from flask import Flask, render_template, jsonify, redirect, request, make_response, session, g
from api import NEWS_API_KEY, STOCK_API_KEY
from forms import LoginForm, SignUpForm
from models import Company, Watchlist, User, connect_db
from newsapi import NewsApiClient
from urllib.request import urlopen
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.exc import IntegrityError
import requests, random, json, os


CURR_USER_KEY = "curr_user"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///stock_market'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "1234hello1234")
connect_db(app)


STOCK_API_URL = "https://www.alphavantage.co/query?"
newsapi = NewsApiClient(api_key=NEWS_API_KEY)


##############################################################################
# NEWS API CALL FUNCTIONS
##############################################################################


def get_company_news(name):
    company = get_company_info(name)
    nname, *inc = company["name"].replace(',',' ').split()
    print(nname)
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
        }
        news_list.append(news)

    return news_list


##############################################################################
# STOCK DATA API CALL FUNCTIONS
##############################################################################


def get_company_info(name):
    url = (f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={name}&apikey={STOCK_API_KEY}")
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
    stock_price_url = (f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=full&symbol={name}&apikey={STOCK_API_KEY}")
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

    return stock_result[0:60]


def get_bollinger_band(name):

    response = urlopen(f"{STOCK_API_URL}function=BBANDS&symbol={name}&interval=daily&time_period=20&series_type=close&nbdevup=2&nbdevdn=2&apikey=f{STOCK_API_KEY}")
    data = response.read().decode("utf-8")
    data_to_json = json.loads(data)
    temp_data = data_to_json["Technical Analysis: BBANDS"]
    bband = []

    for item in temp_data:
        band_data = {
            "date" : item,
            "upper" : temp_data[item]["Real Upper Band"],
            "lower" : temp_data[item]["Real Lower Band"],
            "middle" : temp_data[item]["Real Middle Band"]
        }
        bband.append(band_data.copy())
    return bband[0:60]


@app.route("/api/stock/chart", methods=["POST"])
def send_chart_json_data():

    response = request.get_json()
    result = json.dumps(response)
    res = json.loads(result)
    name = res["name"]

    json_response = {}
    json_response["company"] = get_company_info(name)
    json_response["stock"] = get_stock_data(name)
    json_response["bbands"] = get_bollinger_band(name)
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

    # if not g.user:
    #     return redirect("/signup")
    # else:
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
            flash('Username taken', "danger")
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

# #############################################################################
#

















