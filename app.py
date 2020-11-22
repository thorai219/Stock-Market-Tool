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

    term = request.args.get("q").upper()
    url = (f"{STOCK_API_URL}search?query={term}&limit=5&apikey={STOCK_API_KEY}")
    data = get_jsonparsed_data(url)
    
    results = []

    for item in data:
        results.append((f'{item["symbol"]} - {item["name"]}'))

    return jsonify(matching_results = results)

@app.route("/get/profile", methods=["POST"])
def get_profile():

    if not g.user:
        return redirect('/login')

    ticker = request.json['value']

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

    chart_url = (f"{STOCK_API_URL}historical-chart/1min/{name}?apikey={STOCK_API_KEY}")
    chart = get_jsonparsed_data(chart_url)

    date = []
    price = []

    for item in chart:
        date.append(item["date"])
        price.append(item["close"])

    chart_data = {}
    chart_data["date"] = date
    chart_data["price"] = price

    return make_response(jsonify(chart_data))

@app.route("/add/following", methods=["POST"])
def add_to_following():

    if not g.user:
        return redirect('/')

    symbol = request.json['value']

    query = db.session.query(Following.company_symbol).filter(Following.company_symbol==symbol)
    results = [symbol[0] for symbol in query.all()]

    if len(results) > 0:
        return make_response(jsonify({"msg": "already following!"}))
    else:
        following = Following(
            user_id=g.user.id,
            company_symbol=symbol
        )
        db.session.add(following)
        db.session.commit()

        return make_response(jsonify({"msg": "Added to your watchlist"}))

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

        except IntegrityError:
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

    if not g.user:
        return render_template('/user/welcome.html')

    gainer_obj = get_gainers()
    losers_obj = get_losers()
    
    return render_template(
        "/user/home.html",
        news=get_headline_news(),
        marquee=get_movers(),
        user=g.user,
        gainers=gainer_obj[0:10],
        losers=losers_obj[0:10],
        snp=snp(),
        dow=dow(),
        nasdaq=nasdaq(),
        sector=sector_performance()
    )

@app.route("/watchlist")
def watchlist():

    query = db.session.query(Following.company_symbol).filter(Following.user_id==g.user.id)
    results = [symbol[0] for symbol in query.all()]

    watchlist = []

    for ticker in results:
        url = (f"{STOCK_API_URL}quote-short/{ticker}?apikey={STOCK_API_KEY}")
        watchlist.append(get_jsonparsed_data(url))

    
    return render_template("/user/watchlist.html", watchlist=watchlist, user=g.user)


@app.route("/profile", methods=["GET", "POST"])
def profile():

    if not g.user:
        return redirect("/login")

    form = SignUpForm(obj=g.user)

    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            g.user.username = form.username.data
            g.user.email = form.email.data
            g.user.fullname = form.fullname.data

            db.session.commit()

            flash('Successfully updated information.', "success")
            return redirect("")
        flash("Re-enter password to complete changes.", 'danger')

    return render_template('/user/profile.html', form=form)

@app.route("/delete/profile", methods=["POST"])
def delete_user():

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    else:
        do_logout()

        db.session.delete(g.user)
        db.session.commit()

        flash("Account deleted!", "success")
        return redirect("/signup")

@app.route("/404")
def show_404():

    return render_template("/404.html")