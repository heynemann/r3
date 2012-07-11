#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    redis_host = sys.argv[3]
    redis_port = int(sys.argv[4])
    app.redis_host = redis_host
    app.redis_port = redis_port
    app.run(debug=True, host=host, port=port)

