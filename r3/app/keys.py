#!/usr/bin/python
# -*- coding: utf-8 -*-

ALL_KEYS = 'r3::*'

# MAPPER KEYS
MAPPERS_KEY = 'r3::mappers'
MAPPER_INPUT_KEY = 'r3::jobs::%s::input'
MAPPER_OUTPUT_KEY = 'r3::jobs::%s::%s::output'
MAPPER_ERROR_KEY = 'r3::jobs::%s::errors'
MAPPER_WORKING_KEY = 'r3::jobs::%s::working'
LAST_PING_KEY = 'r3::mappers::%s::last-ping'

# JOB TYPES KEYS
JOB_TYPES_KEY = 'r3::job-types'
JOB_TYPES_ERRORS_KEY = 'r3::jobs::*::errors'
JOB_TYPE_KEY = 'r3::job-types::%s'

# STATS KEYS
PROCESSED = 'r3::stats::processed'
PROCESSED_SUCCESS = 'r3::stats::processed::success'
PROCESSED_FAILED = 'r3::stats::processed::fail'

