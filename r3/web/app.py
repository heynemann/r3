#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/mappers")
def mappers():
    return render_template('mappers.html')

@app.route("/failed")
def failed():
    return render_template('failed.html')

@app.route("/job-types")
def job_types():
    return render_template('job-types.html')

@app.route("/stats")
def stats():
    return render_template('stats.html')

@app.route("/jobs/<job_id>")
def job(job_id):
    return render_template('job.html', job_id=job_id)


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    redis_host = sys.argv[3]
    redis_port = int(sys.argv[4])
    app.redis_host = redis_host
    app.redis_port = redis_port
    app.run(debug=True, host=host, port=port)

