#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 18:53:03 2019

@author: theofieber
"""

from flask import Flask, render_template,send_file
import os

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

FILE_SYSTEM_ROOT = "uploads"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/browser')
def browse():
    itemList = os.listdir(FILE_SYSTEM_ROOT)
    return render_template('browse.html', itemList=itemList)

@app.route('/browser/<path:urlFilePath>')
def browser(urlFilePath):
    nestedFilePath = os.path.join(FILE_SYSTEM_ROOT, urlFilePath)
    if os.path.isdir(nestedFilePath):
        itemList = os.listdir(nestedFilePath)
        if not urlFilePath.startswith("/"):
            urlFilePath = "/" + urlFilePath
        return render_template('browse.html', urlFilePath=urlFilePath, itemList=itemList)
    if os.path.isfile(nestedFilePath):
        print(nestedFilePath)
        return send_file(nestedFilePath,as_attachment=True)
    return 'something bad happened'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
