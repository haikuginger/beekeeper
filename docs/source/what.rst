What?
=====

Recap: The problem is state
---------------------------

The problem with existing solutions isn't that there's something
fundamentally wrong with them from a technical perspective.
They do exactly what they're designed to do, and they do it extremely
well. No one is saying that Requests isn't an excellent HTTP client,
or that its .json() parsing method isn't excruciatingly convenient.
To say that would be to lie.

What's missing from Requests and solutions like it is *state*. Requests
is commonly used to access RESTful APIs, but it doesn't actually know
anything about those APIs. The developer making use of it has to feed
it every variable manually with every request, and there's no clear
mapping between a particular request and the actual resource on the
remote server that it's trying to access.

Clearly, the solution to the problem isn't to make a "better Requests",
or a "better urllib" or a "better cURL". The solution is a library that
can both have knowledge about what a RESTful API looks like, and know
how to map the variables, endpoints, and data types of that API into
an easily-understandable object structure. This means it needs state.

Beekeeper: The answer
---------------------

I've been a bit long-winded up to here, so I'll get to the point quickly.
Beekeeper is a library that does exactly that. By consuming JSON files
that describe the endpoints of an API, the variables that might be
in play, and the way those endpoints relate to real objects and real
actions on the remote server, beekeeper lets you build a client to work
with an entire API with one of code:

.. code:: python

    wiki = API.from_hive_file('wikipedia.json')

And once you have that API client, it's just as easy to do things with it:

.. code:: python

    resp = wiki.Articles['Wisconsin'].get()

Once you're using beekeeper, you don't need to think in terms of endpoints,
or parameters, or headers, or response data formats: you just need to
think about the real objects that exist in the system you're trying to use.

But wait, there's more!
-----------------------

Of course, right now, to get the benefit of this, you typically have to 
write the JSON "hive" file to describe the API yourself. But, with a bit
of help, and a bit of luck, that won't always be the case. The long-term
goal is for beekeeper to become so popular that API providers will
write their own hive files and host them on their own websites. In
the not-too-distant future, initializing an API interface with beekeeper
could be as simple as this:

.. code:: python

    wiki = API.from_domain('wikipedia.org')

Simply by using beekeeper, you'll be able to access any API from any site,
just by typing in the domain name. And, because the hive file is provided
to your application directly by the server, it's constantly up to date
with the latest version of the server's API. (Of course, if you want to
keep using an older version of the hive, the specification provides
for that as well.)

And, since JSON files are easily human-readable too, you can (if you want;
you won't need to anymore) navigate to the hive file in your browser and
take a look to see what goes into making that particular API work.