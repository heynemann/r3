#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, g, redirect, url_for
from ujson import loads

from r3.web.extensions import RedisDB
from r3.version import __version__
from r3.app.utils import flush_dead_mappers
from r3.app.keys import MAPPERS_KEY, JOB_TYPES_KEY, JOB_TYPE_KEY, LAST_PING_KEY, MAPPER_ERROR_KEY, MAPPER_WORKING_KEY, JOB_TYPES_ERRORS_KEY, ALL_KEYS, PROCESSED, PROCESSED_FAILED

app = Flask(__name__)

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
        key = MAPPER_WORKING_KEY % mapper
        working = db.connection.lrange(key, 0, -1)
        if not working:
            mappers_status[mapper] = None
        else:
            mappers_status[mapper] = working

    return mappers_status

def get_all_jobs(all_job_types):
    all_jobs = {}
    for job_type in all_job_types:
        job_type_jobs = db.connection.smembers(JOB_TYPE_KEY % job_type)
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
    error_queues = db.connection.keys(JOB_TYPES_ERRORS_KEY)

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
    key_names = db.connection.keys(ALL_KEYS)

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

    processed = db.connection.get(PROCESSED)
    processed_failed = db.connection.get(PROCESSED_FAILED)

    return render_template('stats.html', info=info, keys=keys, processed=processed, failed=processed_failed)

@app.route("/stats/keys/<key>")
def key(key):
    key_type = db.connection.type(key)

    if key_type == 'list':
        value = db.connection.lrange(key, 0, -1)
        multi = True
    elif key_type == 'set':
        value = db.connection.smembers(key)
        multi = True
    else:
        value = db.connection.get(key)
        multi = False

    return render_template('show_key.html', key=key, multi=multi, value=value)

@app.route("/stats/keys/<key>/delete")
def delete_key(key):
    db.connection.delete(key)
    return redirect(url_for('stats'))
 
@app.route("/jobs/<job_id>")
def job(job_id):
    return render_template('job.html', job_id=job_id)

if __name__ == "__main__":
    app.config.from_object('r3.web.config')
    db = RedisDB(app)
    app.run(debug=True, host=app.config['WEB_HOST'], port=app.config['WEB_PORT'])

