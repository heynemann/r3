r³
==

r³ is a map reduce engine written in python using a redis backend. It's purpose
is to be simple.

r³ has only three concepts to grasp: input streams, mappers and reducers.

The diagram below relates how they interact:

![r³ components interaction](https://github.com/heynemann/r3/raw/master/r3.png)

If the diagram above is a little too much to grasp right now, don't worry. Keep
reading and use this diagram later for reference.

A fairly simple map-reduce example to solve is counting the number of
occurrences of each word in an extensive document. We'll use this scenario as
our example.

Installing
----------

Installing r³ is as easy as:

    pip install r3

After successful installation, you'll have three new commands: `r3-app`,
`r3-map` and `r3-web`.

Running the App
---------------

In order to use r³ you must have a redis database running. Getting one up in
your system is beyond the scope of this document.

We'll assume you have one running at 127.0.0.1, port 7778 and configured to
require the password 'r3' using database 0.

The service that is at the heart of r³ is `r3-app`. It is the web-server that
will receive requests for map-reduce jobs and return the results.

To run `r3-app`, given the above redis back-end, type:

    r3-app --redis-port=7778 --redis-pass=r3 -c config.py

We'll learn more about the configuration file below.

Given that you have a proper configuration file, your r3 service will be
available at `http://localhost:8888`.

As to how we actually perform a map-reduce operation, we'll see that after the
`Running Mappers` section.

App Configuration
-----------------

In the above section we specified a file called `config.py` as configuration.
Now we'll see what that file contains.

The configuration file that we pass to the `r3-app` command is responsible for
specifying `input stream processors` and `reducers` that should be enabled.

Let's see a sample configuration file:

    INPUT_STREAMS = [
        'test.count_words_stream.CountWordsStream'
    ]

    REDUCERS = [
        'test.count_words_reducer.CountWordsReducer'
    ]

This configuration specifies that there should be a `CountWordsStream` input
stream processor and a `CountWordsReducer` reducer. Both will be used by the
`stream` service to perform a map-reduce operation. 

We'll learn more about `input streams` and `reducers` in the sections below.

The input stream
----------------

The input stream processor is the class responsible for creating the input
streams upon which the mapping will occur.

In our counting words in a document sample, the input stream processor class
should open the document, read the lines in the document and then return each
line to `r3-app`.

Let's see a possible implementation:

    from os.path import abspath, dirname, join

    class CountWordsStream:
        job_type = 'count-words'
        group_size = 1000

        def process(self, app, arguments):
            with open(abspath(join(dirname(__file__), 'chekhov.txt'))) as f:
                contents = f.readlines()

            return [line.lower() for line in contents]

The `job_type` property is required and specifies the relationship that this
input stream has with mappers and with a specific reducer.

The `group_size` property specifies how big is an input stream. In the above
example, our input stream processor returns all the lines in the document, but
r³ will group the resulting lines in batches of 1000 lines to be processed by
each mapper. How big is your group size varies wildly depending on what your
mapping consists of.

Running Mappers
---------------

`Input stream processors` and `reducers` are sequential and thus run in-process
in the r³ app. Mappers, on the other hand, are inherently parallel and are run
on their own as independent worker units.

Considering the above example of input stream and reducer, we'll use a
`CountWordsMapper` class to run our mapper.

We can easily start the mapper with:

    r3-map --redis-port=7778 --redis-pass=r3 --mapper-key=mapper-1 --mapper-class="test.count_words_mapper.CountWordsMapper"

The `redis-port` and `redis-pass` arguments require no further explanation.

The `mapper-key` argument specifies a unique key for this mapper. This key 
should be the same once this mapper restarts.

The `mapper-class` is the class r³ will use to map input streams.

Let's see what this map class looks like. If we are mapping lines (what we got
out of the input stream steap), we should return each word and how many times
it occurs.

    from r3.worker.mapper import Mapper

    class CountWordsMapper(Mapper):
        job_type = 'count-words'

        def map(self, lines):
            return list(self.split_words(lines))

        def split_words(self, lines):
            for line in lines:
                for word in line.split():
                    yield word, 1

The `job_type` property is required and specifies the relationship that this
mapper has with a specific input stream and with a specific reducer.

Reducing
--------

The `job_type` property is required and specifies the relationship that this
reducer has with mappers and with a specific input stream.


