r³
==

r³ is a map reduce engine written in python using a redis backend. It's purpose
is to be simple.

r³ has only three concepts to grasp: input streams, mappers and reducers.

The diagram below relates how they interact:

![r³ components interaction](https://github.com/heynemann/r3/raw/master/r3.png)

If the diagram above is a little too much to grasp right now, don't worry. Keep
reading and use this diagram later for reference.

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

Running Mappers
---------------

As you
