import requests, json
from urllib.parse import urlparse, urljoin
from flask import Flask, request, render_template, redirect, url_for, flash, abort,session
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user, UserMixin,
                         confirm_login, fresh_login_required)
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, PasswordField, validators
from passlib.hash import sha256_crypt as pwd_context
#===============================================================================
# From DockerLogin + some changes like RegisterForm and load_user
class LoginForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
                          message=u"Usernames must be between 2-25 characters."),
        validators.InputRequired(u"Forget something?")])
    password = PasswordField("Password", [
        validators.Length(min=2, max=25,
                          message=u"Passwords must be between 2-25 characters."),
        validators.InputRequired(u"Forget something?")])
    remember = BooleanField('Remember me')

class RegisterForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
                          message=u"Usernames must be between 2-25 characters."),
        validators.InputRequired(u"Forget something?")])
    password = PasswordField("Password", [
        validators.Length(min=6, max=25,
                          message=u"Passwords must be between 6-25 characters."),
        validators.InputRequired(u"Forget something?")])

def is_safe_url(target):
    """
    :source: https://github.com/fengsp/flask-snippets/blob/master/security/redirect_back.py
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username
        self.token = "Unknown"

    def set_token(self, token):
        self.token = token
        return self

app = Flask(__name__)
app.secret_key = 'testing1234@#$'

app.config.from_object(__name__)

login_manager = LoginManager()

login_manager.session_protection = "strong"

login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."

login_manager.refresh_view = "login"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    username = session['username']
    if username == None:
        return None
    else:
        token = session['token']
        return User(user_id, username).set_token(token)

login_manager.init_app(app)
#===============================================================================
# Mixed from DockerLogin + some changes in register and login
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit() and request.method == "POST" :
        username = request.form["username"]
        password = request.form["password"]
        # hash password
        password = pwd_context.encrypt(password)
        url = 'http://restapi:5000/register'
        post_request = requests.post(url, data={"username": username, "password": password})
        # if not ok or not created
        if post_request.status_code != 201:
            flash("Registration failed")
            #flash(post_request.json()['message'])
            flash(post_request.status_code)
            flash(post_request.text)
            # flash(username)
        else:
            flash("Successfully registered.")
            flash(post_request.text)
            return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit() and request.method == "POST" and "username" in request.form:
        username = request.form["username"]
        password = request.form["password"]

        #password = pwd_context.encrypt(password)
        url = "http://restapi:5000/token"
        get_request = requests.get(url, data={"username": username, "password": password})

        #url = "http://restapi:5000/token?username="+username+"&password="+password
        #get_request = requests.get(url)
        if get_request.status_code != 401:
            remember = request.form.get("remember", "false") == "true"
            gr_json = get_request.json()
            #gr_json = json.loads(get_request.json())
            user = User(int(gr_json['id']), username).set_token(gr_json['token'])
            if login_user(user, remember=remember):
                session['username'] = username
                session['token'] = gr_json['token']
                flash("Logged in!")
                flash("I'll remember you") if remember else None
                next = request.args.get("next")
                if not is_safe_url(next):
                    abort(400)
                return redirect(next or url_for('index'))
            else:
                flash("Sorry, but you could not log in.")
        else:
            flash(get_request.status_code)
            flash(get_request.text)
            flash(u"Invalid username or password.")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))

@app.route("/secret")
@login_required
def secret():
    return render_template('secret.html')
#===============================================================================
# Adapted from the function "getACPTimesData" from index.php from P6
@app.route('/output')
@login_required
def output():
    token = current_user.token
    url = 'http://restapi:5000'
    if request.args.get('top', type=int):
        top = request.args.get('top', type=int)
    else:
        top = 0
    dtype = request.args.get('dtype', type=str)
    output = request.args.get('output', type=str)
    # get desired output
    if output == 'all':
        url += '/listAll'
    elif output == 'open':
        url += '/listOpenOnly'
    elif output == 'close':
        url += '/listCloseOnly'
    # get data type
    if dtype == 'csv':
        url += '/csv'
    else:
        url += '/json'
    # get top k to display
    if top > 0:
        url += '?top=' + str(top)
    url += '&token=' + token
    data = requests.get(url).text
    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
