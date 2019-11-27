# -*- coding:ISO-8859-1 -*-
from flask import Flask
from flask_compress import Compress
from .secrets import SECRET_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_PATH'] = 10000000
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 24*3600*7
Compress(app)

from app import routes
