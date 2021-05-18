from flask import Flask, make_response, redirect, request, Response, render_template, url_for, flash, g
from flask_mail import Mail, Message
from flask_sslify import SSLify
from flask_session import Session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy, Pagination
from sqlalchemy import text, and_, exc, func, desc
from database import db_session, init_db
from models import User, RadioData
from celery import Celery
import config
import random
import datetime
import hashlib
import time
import redis
import re
import uuid
import requests
import logging

# debug
debug = True
timeout = 0.50

# app config
app = Flask(__name__)
# sslify = SSLify(app)
app.config["SECRET_KEY"] = config.SECRET_KEY

# session persistence
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.from_url("redis://localhost:6379/0")
app.config["SESSION_PERMANENT"] = True
sess = Session()
sess.init_app(app)

# Flask-Mail configuration
app.config["MAIL_SERVER"] = "smtp.mail.me.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = config.MAIL_USERNAME
app.config["MAIL_PASSWORD"] = config.MAIL_PASSWORD
app.config["MAIL_DEFAULT_SENDER"] = config.MAIL_DEFAULT_SENDER

# SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS

# define our login_manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/auth/login"
login_manager.login_message = "Login required to access this site."
login_manager.login_message_category = "primary"

# disable strict slashes
app.url_map.strict_slashes = False

# Celery config
app.config["CELERY_BROKER_URL"] = config.CELERY_BROKER_URL
app.config["CELERY_RESULT_BACKEND"] = config.CELERY_RESULT_BACKEND
app.config["CELERY_ACCEPT_CONTENT"] = config.CELERY_ACCEPT_CONTENT
app.config.update(accept_content=["json", "pickle"])

# Initialize Celery
celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)

# Config mail
mail = Mail(app)

# gunicorn logging
gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

# on the apps first startup, init the db
@app.before_first_request
def create_db():
    """
    Create and init the database
    :return initialized database from models.py
    """
    today = get_date()
    init_db()
    app.logger.info("SQLite3 Database initialized on: {}".format(today))

    users = db_session.query(User).count()
    if users == 0:
        # load default user
        user = User("Craig", "Derington", "craigderington", "yufakay3!", "craig.derington@mac.com")
        db_session.add(user)
        db_session.commit()
        db_session.flush()
    
    

# clear all db sessions at the end of each request
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
    app.logger.info("Database session destroyed.")


# load the user
@login_manager.user_loader
def load_user(id):
    try:
        return db_session.query(User).get(int(id))
        app.logger.info("Querying for User: {}".format(str(id)))
    except exc.SQLAlchemyError as err:
        app.logger.warning("Could not load User: {} error: {}".format(str(id), str(err)))
        return None


# run before each request
@app.before_request
def before_request():
    g.user = current_user


# default routes
@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    """
    Receiver debug page
    """
    radiodata = None

    try:
        radiodata = db_session.query(RadioData).order_by(
            RadioData.created_on.desc()
        ).limit(50)

        totals = db_session.query(RadioData).count()

    except exc.SQLAlchemyError as db_err:
        flash("{}".format(str(db_err)))
        return redirect(url_for("index"))
    
    return render_template(
        "index.html",
        radiodata=radiodata,
        totals=totals,
        today=get_date()
    )


@app.route("/auth/login", methods=["GET", "POST"])
def login():
    """
    Login user page
    """
    return render_template(
        "login.html", 
        today=get_date()
    )


@app.route('/logout', methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.errorhandler(404)
def page_not_found(err):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(err):
    return render_template("500.html"), 500


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


def get_date():
    # set the current date time for each page
    today = datetime.datetime.now().strftime("%c")
    return "{}".format(today)


@app.template_filter("formatdate")
def format_date(value):
    dt = value
    return dt.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    port = config.APP_PORT
    debug = config.DEBUG
    
    # start the application
    app.run(
        debug=debug,
        port=port
    )

