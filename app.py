from flask import Flask, render_template, flash, jsonify, redirect, request, make_response, session, g
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from forms import LoginForm, SignUpForm
from models import db, connect_db, User, Company, Following
from sqlalchemy.exc import IntegrityError
from urllib.request import urlopen
from datetime import date,datetime, timedelta
from urllib import parse
from api import STOCK_API_KEY
import json, requests

CURR_USER_KEY = "curr_user"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///stock_market'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "1234hello1234"
toolbar = DebugToolbarExtension(app)

connect_db(app)

STOCK_API_URL = "https://financialmodelingprep.com/api/v3/"


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


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#   USER SECTION
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Sign up a user add to database with encrypted password"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = SignUpForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                fullname=form.fullname.data,
                password=form.password.data,
                email=form.email.data
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('user/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('user/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            return redirect("/")
        else:
            flash("Invalid credentials.", 'danger')

    return render_template('user/login.html', form=form)

@app.route('/logout')
def logout():

    do_logout()

    return redirect('/')


@app.route('/news')
def show_news():

    news = get_headline_news()

    return render_template('user/home.html', news=news)


@app.route('/')
def homepage():

    if  g.user:

        query = db.session.query(Following.company_symbol).filter(
            Following.user_id == g.user.id
        )
        following = [cs[0] for cs in query.all()]

        result = []

        for symbol in following:
            result.append(get_quote(symbol))
        return render_template('user/mypage.html', user=g.user, following=result)
    
    else:
        return redirect('/signup')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#   API SECTION
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def get_jsonparsed_data(url):

    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

def query_db_for_symbol(term):

    query = db.session.query(Company.symbol).filter(or_(
        Company.name.ilike("%" + term + "%"),
        Company.name == term,
        Company.symbol == term
    ))

    res = [cn[0] for cn in query.all()]
    symbol = str(res[0]).strip("[' ']")

    return symbol

def get_quote(symbol):

    url = (f"{STOCK_API_URL}quote-short/{symbol}?apikey={STOCK_API_KEY}")
    quote = get_jsonparsed_data(url)

    return quote

def get_company_profile(symbol):

    url = (f"{STOCK_API_URL}profile/{symbol}?apikey={STOCK_API_KEY}")

    profile = get_jsonparsed_data(url)

    return profile

def get_todays_data(data):

    chart = []

    todays_date = date.today()
    today = todays_date.strftime("%Y-%m-%d")
    yesterday = date.today() - timedelta(days = 1)
    
    for item in data:
        time = item["date"][0:10]
        if time == today:
            chart_data = {
                "date" : item["date"],
                "price" : item["close"]
            }
            chart.append(chart_data.copy())
    return chart

def get_headline_news():

    news_url = (f"{STOCK_API_URL}stock_news?limit=20&apikey={STOCK_API_KEY}")
    news = get_jsonparsed_data(news_url)

    return news

def get_company_news(symbol):

    news_url = (f"{STOCK_API_URL}stock_news?tickers={symbol}&limit=20&apikey={STOCK_API_KEY}")
    news = get_jsonparsed_data(news_url)

    return news

@app.route("/index")
def get_index():

    snp_url = (f"{STOCK_API_URL}historical-chart/5min/%5EGSPC?apikey={STOCK_API_KEY}")
    dow_url = (f"{STOCK_API_URL}historical-chart/5min/%5EDJI?apikey={STOCK_API_KEY}")
    nasdaq_url = (f"{STOCK_API_URL}historical-chart/5min/%5EIXIC?apikey={STOCK_API_KEY}")

    snp_res = get_jsonparsed_data(snp_url)
    dow_res = get_jsonparsed_data(dow_url)
    nasdaq_res = get_jsonparsed_data(nasdaq_url)

    data = {}
    data["snp"] = get_todays_data(snp_res)
    data["dow"] = get_todays_data(dow_res)
    data["nasdaq"] = get_todays_data(nasdaq_res)

    return make_response(jsonify(data))

@app.route("/search/company", methods=["POST"])
def get_company_info():

    data = {}

    req = request.get_json()
    name = req["name"]
    symbol = query_db_for_symbol(name)

    chart_url = (f"{STOCK_API_URL}historical-chart/1min/{symbol}?apikey={STOCK_API_KEY}")
    chart_res = get_jsonparsed_data(chart_url)

    data["chart"] = get_todays_data(chart_res)
    data["news"] = get_company_news(symbol)
    data["profile"] = get_company_profile(symbol)

    return make_response(jsonify(data))

@app.route("/api/auto/search")
def auto_complete_search():

    term = request.args.get("q")
    print(term)    
    query = db.session.query(Company.name).filter(or_(
            Company.name.ilike("%" + str(term) + "%"),
            Company.name == str(term),
        )).limit(5)
    results = [cn[0] for cn in query.all()]

    return jsonify(matching_results = results)

@app.route("/movers")
def get_movers():

    actives = (f"{STOCK_API_URL}actives?apikey={STOCK_API_KEY}")
    result = get_jsonparsed_data(actives)


    return make_response(jsonify(result))

@app.route("/add/following/<symbol>")
def add_to_following(symbol):

    if not g.user:
        return redirect('/')

    following = Following(
        user_id=g.user.id,
        company_symbol=symbol
    )
    db.session.add(following)
    db.session.commit()

    return redirect("/")

@app.route("/get/stock", methods=["POST"])
def get_stock():

    data = {}

    req = request.get_json()
    symbol = req["symbol"]
    print(symbol)

    chart_url = (f"{STOCK_API_URL}historical-chart/1min/{symbol}?apikey={STOCK_API_KEY}")
    chart_res = get_jsonparsed_data(chart_url)

    data["chart"] = get_todays_data(chart_res)
    data["news"] = get_company_news(symbol)
    data["profile"] = get_company_profile(symbol)

    return make_response(jsonify(data))