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
import json, requests, os

CURR_USER_KEY = "curr_user"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgres:///stock_market')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
STOCK_API_KEY = os.environ.get('STOCK_API_KEY', STOCK_API_KEY)
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hefedelaspldas1122333fas')
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


#########################################
# API FUNCTIONS

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

def get_movers():

    actives_url = (f"{STOCK_API_URL}actives?apikey={STOCK_API_KEY}")
    movers = get_jsonparsed_data(actives_url)

    return movers

def get_headline_news():

    news_url = (f"{STOCK_API_URL}stock_news?limit=20&apikey={STOCK_API_KEY}")
    news = get_jsonparsed_data(news_url)

    return news

def get_gainers():

    gainers_url = (f"{STOCK_API_URL}gainers?apikey={STOCK_API_KEY}")
    gainers = get_jsonparsed_data(gainers_url)

    return gainers

def get_losers():

    losers_url = (f"{STOCK_API_URL}losers?apikey={STOCK_API_KEY}")
    losers = get_jsonparsed_data(losers_url)

    return losers

def sector_performance():

    sector_url = (f"{STOCK_API_URL}sectors-performance?apikey={STOCK_API_KEY}")
    sector = get_jsonparsed_data(sector_url)

    return sector

def get_company_profile(symbol):

    url = (f"{STOCK_API_URL}profile/{symbol}?apikey={STOCK_API_KEY}")
    profile = get_jsonparsed_data(url)

    return profile

def get_company_financials(symbol):

    url = (f"{STOCK_API_URL}income-statement/{symbol}?limit=1&apikey={STOCK_API_KEY}")
    financials = get_jsonparsed_data(url)

    return financials

def get_company_rating(symbol):

    url = (f"{STOCK_API_URL}grade/{symbol}?limit=7&apikey={STOCK_API_KEY}")
    rating = get_jsonparsed_data(url)

    return rating

def snp():

    snp_url = (f"{STOCK_API_URL}quote/%5EGSPC?apikey={STOCK_API_KEY}")
    snp = get_jsonparsed_data(snp_url)

    snp_obj = {}
    snp_obj['changesPercentage'] = str(snp[0]['changesPercentage'])
    snp_obj['name'] = snp[0]['name']
    snp_obj['price'] = snp[0]['price']
    snp_obj['change'] = str(snp[0]['change'])

    return snp_obj

def dow():

    dow_url = (f"{STOCK_API_URL}quote/%5EDJI?apikey={STOCK_API_KEY}")
    dow = get_jsonparsed_data(dow_url)

    dow_obj = {}
    dow_obj['changesPercentage'] = str(dow[0]['changesPercentage'])
    dow_obj['name'] = dow[0]['name']
    dow_obj['price'] = dow[0]['price']
    dow_obj['change'] = str(dow[0]['change'])

    return dow_obj

def nasdaq():

    nasdaq_url = (f"{STOCK_API_URL}quote/%5EIXIC?apikey={STOCK_API_KEY}")
    nasdaq = get_jsonparsed_data(nasdaq_url)

    nasdaq_obj = {}
    nasdaq_obj['changesPercentage'] = str(nasdaq[0]['changesPercentage'])
    nasdaq_obj['name'] = nasdaq[0]['name']
    nasdaq_obj['price'] = nasdaq[0]['price']
    nasdaq_obj['change'] = str(nasdaq[0]['change'])

    return nasdaq_obj

@app.route("/search")
def auto_complete_search():

    term = request.args.get("q")
    query = db.session.query(Company.name).filter(or_(
                Company.name.ilike("%" + str(term) + "%"),
                Company.name == str(term),
            )).limit(5)
    results = [cn[0] for cn in query.all()]

    return jsonify(matching_results = results)

@app.route("/get/profile", methods=["POST"])
def get_profile():

    if not g.user:
        return redirect('/login')

    name = request.json['value']

    if name == '':
        return render_template('404.html')
    ticker = query_db_for_symbol(name)

    profile = {}
    profile["company"] = get_company_profile(ticker)
    profile["rating"] = get_company_rating(ticker)
    profile["financial"] = get_company_financials(ticker)

    return make_response(jsonify(profile))
    
@app.route("/search/ticker", methods=["POST"])
def get_company_info():

    if not g.user:
        return redirect('/login')

    name = request.json['value']

    if name == '':
        return render_template('404.html')
    ticker = query_db_for_symbol(name)

    chart_url = (f"{STOCK_API_URL}historical-chart/1min/{ticker}?apikey={STOCK_API_KEY}")
    chart = get_jsonparsed_data(chart_url)


    return make_response(jsonify(chart))
    
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

@app.route("/long/polling/snp")
def snp_long_polling():

    return snp()

@app.route("/long/polling/dow")
def dow_long_polling():

    return dow()

@app.route("/long/polling/nasdaq")
def nasdaq_long_polling():

    return nasdaq()

#########################################
# USER SIGNUP/LOGIN

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Sign up a user add to database with encrypted password"""

    if g.user:
        return redirect('/login')

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

@app.route('/movers')
def show_gainers():

    if not g.user:
        return redirect('/login')

    return render_template(
        "user/movers.html",
        snp=snp(),
        dow=dow(),
        nasdaq=nasdaq(),
        marquee=get_movers(),
        gainers=get_gainers(),
        losers=get_losers(),
        sector=sector_performance()
    )


#########################################
# NAVIGATION

@app.route("/")
def homepage():

    gainer_obj = get_gainers()
    losers_obj = get_losers()
    snp()

    return render_template(
        "/user/home.html",
        news=get_headline_news(),
        marquee=get_movers(),
        gainers=gainer_obj[0:10],
        losers=losers_obj[0:10],
        snp=snp(),
        dow=dow(),
        nasdaq=nasdaq(),
        sector=sector_performance()
    )