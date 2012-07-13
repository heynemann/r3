#!/usr/bin/python
# -*- coding: utf-8 -*-

import random

from flask import Flask, render_template, g

from r3.web.extensions import RedisDB
from r3.version import __version__

app = Flask(__name__)

def server_context():
    return {
        'mappers': [],
        'job_types': [],
        'r3_service_status': 'running',
        'r3_version': __version__
    }

@app.before_request
def before_request():
    g.config = app.config
    g.server = server_context()

@app.route("/")
def index():
    failing = random.randint(1,2)
    return render_template('index.html', failed_warning=failing == 1)

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
    info = db.connection.info()
    keys = db.connection.keys('r3::*')
    return render_template('stats.html', info=info, keys=keys)

@app.route("/jobs/<job_id>")
def job(job_id):
    return render_template('job.html', job_id=job_id)


if __name__ == "__main__":
    app.config.from_object('r3.web.config')
    db = RedisDB(app)
    app.run(debug=True, host=app.config['WEB_HOST'], port=app.config['WEB_PORT'])

