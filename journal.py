#!/usr/bin/python

# journal.py
#
# Web application for journal writing
#
# David Gardner
#

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World'
