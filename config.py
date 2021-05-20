import os


basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True

# secrets
SECRET_KEY = os.urandom(64)

# socket server listening + port
RECEIVER_HOST = "0.0.0.0"
RECEIVER_PORT = 7182

# flask app frontend port
APP_PORT = 7181

# Sync to Gateway URL
PORTAL_SYNC_URL = "https://httpbin.org/post"

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = "sqlite:///" + basedir + "radiodata.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Celery
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = "pickle,json"

# Flask-WTF flag for CSRF
CSRF_ENABLED = True

# App name
APP_NAME = "CircuitNimble Python Asyncio Socket Server"

# Flask Mail
MAIL_USERNAME = "craig.derington@mac.com"
MAIL_PASSWORD = ""
MAIL_DEFAULT_SENDER = "craig.derington@mac.com"
MAIL_USE_TLS = True



