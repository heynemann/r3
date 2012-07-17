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


