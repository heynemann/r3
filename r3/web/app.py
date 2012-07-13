#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, g, redirect, url_for
from ujson import loads

from r3.web.extensions import RedisDB
from r3.version import __version__
from r3.app.utils import flush_dead_mappers

app = Flask(__name__)

MAPPERS_KEY = 'r3::mappers'
JOB_TYPES_KEY = 'r3::job-types'
LAST_PING_KEY = 'r3::mappers::%s::last-ping'
MAPPER_ERROR_KEY = 'r3::jobs::%s::errors'

def server_context():
    return {
        'r3_service_status': 'running',
        'r3_version': __version__
    }

@app.before_request
def before_request():
    g.config = app.config
    g.server = server_context()
    g.job_types = db.connection.smembers(JOB_TYPES_KEY)
    g.jobs = get_all_jobs(g.job_types)
    g.mappers = get_mappers()

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

def get_all_jobs(all_job_types):
    all_jobs = {}
    for job_type in all_job_types:
        job_type_jobs = db.connection.smembers('r3::job-types::%s' % job_type)
        all_jobs[job_type] = []
        if job_type_jobs:
            all_jobs[job_type] = job_type_jobs

    return all_jobs

def get_errors():
    errors = []
    for job_type in g.job_types:
        errors = [loads(item) for key, item in db.connection.hgetall(MAPPER_ERROR_KEY % job_type).iteritems()]

    return errors

@app.route("/")
def index():
    error_queues = db.connection.keys('r3::jobs::*::errors')

    has_errors = False
    for queue in error_queues:
        if db.connection.hlen(queue) > 0:
            has_errors = True

    flush_dead_mappers(db.connection, MAPPERS_KEY, LAST_PING_KEY)

    return render_template('index.html', failed_warning=has_errors)

@app.route("/mappers")
def mappers():
    flush_dead_mappers(db.connection, MAPPERS_KEY, LAST_PING_KEY)
    return render_template('mappers.html')

@app.route("/failed")
def failed():
    return render_template('failed.html', errors=get_errors())

@app.route("/failed/delete")
def delete_all_failed():
    for job_type in g.job_types:
        key = MAPPER_ERROR_KEY % job_type
        db.connection.delete(key)

    return redirect(url_for('failed'))

@app.route("/failed/delete/<job_id>")
def delete_failed(job_id):
    for job_type in g.job_types:
        key = MAPPER_ERROR_KEY % job_type
        if db.connection.hexists(key, job_id):
            db.connection.hdel(key, job_id)

    return redirect(url_for('failed'))

@app.route("/job-types")
def job_types():
    return render_template('job-types.html')

@app.route("/stats")
def stats():
    info = db.connection.info()
    key_names = db.connection.keys('r3::*')

    keys = []
    for key in key_names:
        key_type = db.connection.type(key)

        if key_type == 'list':
            size = db.connection.llen(key)
        elif key_type == 'set':
            size = db.connection.scard(key)
        else:
            size = 1

        keys.append({
            'name': key,
            'size': size,
            'type': key_type
        })

    return render_template('stats.html', info=info, keys=keys)

@app.route("/jobs/<job_id>")
def job(job_id):
    return render_template('job.html', job_id=job_id)

if __name__ == "__main__":
    app.config.from_object('r3.web.config')
    db = RedisDB(app)
    app.run(debug=True, host=app.config['WEB_HOST'], port=app.config['WEB_PORT'])

