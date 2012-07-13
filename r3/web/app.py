#!/usr/bin/python
# -*- coding: utf-8 -*-

import random

from flask import Flask, render_template, g

from r3.web.extensions import RedisDB
from r3.version import __version__
from r3.app.utils import flush_dead_mappers

app = Flask(__name__)

MAPPERS_KEY = 'r3::mappers'
JOB_TYPES_KEY = 'r3::job-types'
LAST_PING_KEY = 'r3::mappers::%s::last-ping'

def server_context():
    return {
        'r3_service_status': 'running',
        'r3_version': __version__
    }

@app.before_request
def before_request():
    g.config = app.config
    g.server = server_context()

def get_mappers():
    all_mappers = db.connection.smembers(MAPPERS_KEY)
    mappers_status = {}
    for mapper in all_mappers:
        key = 'r3::mappers::%s::working' % mapper
        working = db.connection.get(key)
        if not working:
            mappers_status[mapper] = None
        else:
            mappers_status[mapper] = working

    return mappers_status

@app.route("/")
def index():
    error_queues = db.connection.keys('r3::jobs::*::errors')

    has_errors = False
    for queue in error_queues:
        if db.connection.llen(queue) > 0:
            has_errors = True

    flush_dead_mappers(db.connection, MAPPERS_KEY, LAST_PING_KEY)
    all_mappers = get_mappers()
    all_job_types = db.connection.smembers(JOB_TYPES_KEY)

    all_jobs = {}
    for job_type in all_job_types:
        all_jobs[job_type] = []

    return render_template('index.html', failed_warning=has_errors, mappers=all_mappers, job_types=all_job_types, jobs=all_jobs)

@app.route("/mappers")
def mappers():
    flush_dead_mappers(db.connection, MAPPERS_KEY, LAST_PING_KEY)
    all_mappers = get_mappers()
    all_job_types = db.connection.smembers(JOB_TYPES_KEY)

    return render_template('mappers.html', mappers=all_mappers, job_types=all_job_types)

@app.route("/failed")
def failed():
    return render_template('failed.html')

@app.route("/job-types")
def job_types():
    all_job_types = db.connection.smembers(JOB_TYPES_KEY)

    all_jobs = {}
    for job_type in all_job_types:
        all_jobs[job_type] = []

    return render_template('job-types.html', job_types=all_job_types, jobs=all_jobs)

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

