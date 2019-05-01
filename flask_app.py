
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="cs232av",
    password="Computer1",
    hostname="cs232av.mysql.pythonanywhere-services.com",
    databasename="cs232av$comments",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.secret_key = "asdfghjkl"
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()


class Carts(db.Model):

    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(4096))

class Comment(db.Model):

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    cid = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    posted = db.Column(db.DateTime, default=datetime.now)
    commenter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    commenter = db.relationship('User', foreign_keys=commenter_id)

class Food(db.Model):

    __tablename__ = "foods"

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(4096))
    cid = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    price = db.Column(db.Float, nullable = False)
    posted = db.Column(db.DateTime, default=datetime.now)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", comments=Comment.query.all())

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    comment = Comment(content=request.form["contents"], cid=request.form["cid"], commenter=current_user)

    db.session.add(comment)
    db.session.commit()

    return redirect(url_for('index'))

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    user = load_user(request.form["username"])
    if user is None:
        return render_template("login_page.html", error=True)

    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    login_user(user)
    return redirect(url_for('index'))

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/signup/", methods=["GET","POST"])
def signup():
    if request.method == "GET":
        return render_template("signup_page.html", userinfo=User.query.all())

    userinfo = User(username=request.form["newuser"], password_hash= generate_password_hash(request.form["newpass"]))

    db.session.add(userinfo)
    db.session.commit()

    return redirect(url_for('login'))

@app.route("/carts")
def carts():
    return render_template("carts_page.html", carts=Carts.query.all())

@app.route("/carts/<cid>", methods=["GET","POST"])
def cartComments(cid):
    if request.method == "GET":
        comments = Comment.query.filter_by(cid=cid)
        cartName = Carts.query.filter_by(id=cid)
        foods = Food.query.filter_by(cid=cid)
        return render_template("carts_page.html", carts=Carts.query.all(), comments=comments, cartName=cartName, foods=foods)

    if not current_user.is_authenticated:
        return redirect(url_for('carts'))

    if request.method == "POST":
        comment = Comment(content=request.form["contents"], cid=cid, commenter=current_user)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('cartComments', cid=cid))

@app.route("/addCart", methods=["GET","POST"])
def addCart():
    if request.method == "GET":
        return render_template("addCart_page.html")

    if request.method == "POST":
        cart = Carts(name=request.form["name"])
        db.session.add(cart)
        db.session.commit()
        return redirect(url_for('carts'))

@app.route("/food")
def food():
    return render_template("food_page.html", foods=Food.query.all())

@app.route("/food/<fname>", methods=["GET"])
def foodList(fname):
    if request.method == "GET":
        cartsPrices = Food.query.filter_by(fname=fname)
        return render_template("food_page.html", foods=Food.query.all(), cartsPrices=cartsPrices, fname=fname)

#    @app.route("/price", methods=["GET"])
#    def foodList(fname):
#        if request.method == "GET":
#            cartsPrices = Food.query.filter_by(fname=fname)
#            return render_template("food_page.html", foods=Food.query.all(), cartsPrices=cartsPrices)

@app.route("/menu")
def menu():
    return render_template("menu_page.html", carts=Carts.query.all())

@app.route("/menu/<cid>", methods=["GET","POST"])
def cartMenu(cid):
    if request.method == "GET":
        cartName = Carts.query.filter_by(id=cid)
        foods = Food.query.filter_by(cid=cid)
        return render_template("menu_page.html", carts=Carts.query.all(), cartName=cartName, foods=foods)

@app.route("/map")
def map():
    return render_template("maptest_page.html")

@app.route("/addfood/<cid>", methods=["GET","POST"])
def addFood(cid):
    if request.method == "GET":
        cartName = Carts.query.filter_by(id=cid)
        menu = Food.query.filter_by(cid=cid)
        return render_template("addfood_page.html", foods=Food.query.all(), cartName=cartName, menu=menu)

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":
        food = Food(cid=cid, fname=request.form["selectFood"], price=request.form["price"])
        db.session.add(food)
        db.session.commit()
        return redirect(url_for('cartComments', cid=cid))
