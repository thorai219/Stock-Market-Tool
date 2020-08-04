from Flask import flask, render_template, redirect, session, g, request, url_for
from api import API_KEY
import requests


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgres:///stock_market'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "hello1234")

connect_db(app)
##############################################################################
# Stock Information

def get_data(ticker):



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




