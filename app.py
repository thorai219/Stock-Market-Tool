from flask import Flask, render_template, jsonify, redirect, request, make_response, session, g
from api import NEWS_API_KEY, STOCK_API_KEY
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, SignUpForm
from models import Company, Watchlist, User, connect_db, db
from newsapi import NewsApiClient
from urllib.request import urlopen
from urllib import parse
from datetime import date, datetime
from sqlalchemy import or_
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

STOCK_API_URL = "https://financialmodelingprep.com/api/v3/"
newsapi = NewsApiClient(api_key=NEWS_API_KEY)


##############################################################################
# NEWS API CALL FUNCTIONS
##############################################################################


# def get_company_news(name):
#     company = get_company_info(name)
#     nname, *inc = company["name"].replace(',',' ').split()
#     company_news = newsapi.get_everything(q=f'{nname}',
#                                           language='en',
#                                           )
#     temp = company_news["articles"] 
#     news_list = []
#     for item in temp:
#         news = {
#             "title" : item["title"],
#             "description" : item["description"],
#             "url" : item["url"],
#             "urlToImage" : item["urlToImage"],
#             "publishedAt" : item["publishedAt"]
#         };
#         news_list.append(news)
#     return news_list


# ##############################################################################
# # STOCK DATA API CALL FUNCTIONS
# ##############################################################################

def get_jsonparsed_data(url):

    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

@app.route("/get/ticker/sector")
def get_carousel_ticker():

    url = (f"{STOCK_API_URL}sectors-performance?apikey={STOCK_API_KEY}")
    data = get_jsonparsed_data(url)
    return make_response(jsonify(data))

@app.route("/get/index/snp")
def get_snp():

    url = (f"{STOCK_API_URL}historical-chart/30min/%5EGSPC?apikey={STOCK_API_KEY}")
    data = get_jsonparsed_data(url)
    return make_response(jsonify(data))

@app.route("/get/index/dow")
def get_dow():
    url = (f"{STOCK_API_URL}historical-chart/30min/%5EDJI?apikey={STOCK_API_KEY}")
    data = get_jsonparsed_data(url)
    return make_response(jsonify(data))

@app.route("/get/index/nasdaq")
def get_nasdaq():
    url = (f"{STOCK_API_URL}historical-chart/30min/%5EIXIC?apikey={STOCK_API_KEY}")
    data = get_jsonparsed_data(url)
    return make_response(jsonify(data))

@app.route("/api/get/chart")
def get_chart():
    data = request.get_json()
    query = db.session.get_or_404(Company.name == data[0])
    print(query)
    # url = (f"{STOCK_API_URL}historical-chart/5min/{term}?apikey={STOCK_API_KEY}")
    # data = get_jsonparsed_data(url)
    return make_response(jsonify(data))

##############################################################################
# AUTO COMPLETE
##############################################################################

@app.route("/api/auto/search")
def auto_complete_search():
    term = request.args.get("q")    
    query = db.session.query(Company.name).filter(or_(
            Company.name.ilike("%" + str(term) + "%"),
            Company.name == str(term),
        )).limit(5)
    results = [cn[0] for cn in query.all()]
    print(results)
    return jsonify(matching_results = results)

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
        return redirect("/login")
    else:
        return render_template("users/main.html")

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

        return render_template("users/homepage.html")

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
                return redirect("/login")

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():

    do_logout()

    return redirect("/login")



@app.route("/show/main/page")
def show_main_page():
    return render_template("/users/main.html")

