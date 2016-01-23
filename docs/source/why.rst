Why?
====

First Principles
----------------

In 2000, as his dissertation, Roy Fielding, one of the cofounders of
the Apache open source HTTP server project, proposed a new standard
for Internet-facing APIs. Rather than having proprietary communications
protocols spewing complicated binary data back and forth, Fielding
thought that communications should take place over HTTP, using HTTP
standard forms of communication, and using representations of the
state of the application, rather than actually transmitting the
application's state. This document describes what we now know as REST
APIs, and it is fundamental to how the Internet works today.

One of the key principles of REST APIs is that each request contains
within itself all of the context needed to act on that request -- and
each response is similar. There are no "sessions" in REST APIs; a
request sent one time should do exactly the same thing if sent again.
This simplifies some things, but complicates others.

Another key principle written by Fielding in his paper was the concept
of "Hypermedia as the Engine of Application State", or HATEOAS. The idea
was that a client application could automatically "discover" all of the
resources that an API provided, as well as the methods and variables
exposed to work with those resources. If the state of the server changed,
and one of those methods was no longer available, then the client library
would become aware of that as part of the normal course of operations;
similarly, a new resource would be immediately available for consumption.

Simplification
--------------

The use of idempotent operations (the same action should have the same
result) and of context wholly contained within the request significantly
simplifies serverside programming. Rather than maintaining a table full
of active session information for its clients, a server only needs to
maintain its internal state, and then know how to map particular
requests to the relevant return data based on the variables it receives.
For example, a server that receives a "GET" request at the "Widgets"
endpoint, with an ID parameter of 123 can simply know that it should
query the Widgets table of its database and return the entry with an
internal ID of 123.

This also simplifies things for the client. Rather than having to
maintain an idea about "where" in the application it is, it creates an
entirely new session with every request, and each request is not affected
by any other request, except insofar as the other request might change
the global state of the application. When using a REST API, the application
can be confident that, in general, requests don't need to be performed
in any particular order.

Complication
------------

While RESTful principles certainly make communication simpler, there are
still some missing pieces. RESTful requests are made over HTTP; we know
that. However, there are any number of different ways to do that, and
almost every single one has been used by some API, in some form or
another. And, what's worse, HATEOAS has not been widely implemented,
although it would have solved many of these difficulties.

As a result, when working with RESTful APIs, developers have to spend
significant periods of time interpreting exactly what the request for a
particular resource ought to have in order to be properly interpreted
by that particular API. Since the code becomes largely specific to the
task at hand, it can't be reused for other purposes, even though the
protocols for communication between various REST APIs are, at a base level,
quite similar.

The developers of each API might also have a specific idea of what a
REST API ought to look like, and might push that agenda by forming their
API in a particular way, or with a particular style. This makes the issue
even more difficult, by causing APIs to have less and less in common.

Existing Solutions
------------------

There are some solutions today that aim to make working with REST APIs
simpler and easier. The largest of these in Python is the "Requests"
library. Requests aims to simplify making RESTful requests by condensing
commonly-used resources into a single library, and stitching them together
so that they can be used within a single line of code. For example:

.. code:: python

    resp = Requests.get('domain.tld/api/resource').json()

The above code succinctly describes exactly what the developer wants
to do - and then does it. It uses the HTTP GET method at the web address
"domain.told/api/resource", takes the response, and parses it from the
JSON format into a native-Python dictionary. Requests also provides other
useful features, like cookie persistence across a session, and automatic
handling of URL parameters and headers.

However, it doesn't actually deal with any of the fundamental problems
that are at play in modern REST APIs. Does it make it easier to work
within the constraints of the existing system? Sure. But because the
Requests library is as fundamentally stateless as the APIs it's interacting
with, it has no way of eliminating them entirely. A variable that's
defined as being passed in a URL parameter must be passed to Requests
as a URL parameter, or the request won't work.

The Problem Remains
-------------------

What's more, many modern REST APIs don't do a good job of descriptively
converting their internal state's object hierarchy into a set of resource
URLs that can be accessed programmatically. This is best exemplified
by Wikipedia, whose REST API has but a single endpoint, which accesses
any resource according to the parameters passed to it:

.. code::

    https://en.wikipedia.org/w/api.php

To access any resources on the API, the developer has to delve into the
(often-lacking) API documentation and figure out exactly what parameters
are needed for which resources. She then has to build a class or method
that encodes that information into a programmatic form for later use,
because knowing that

.. code::

    https://en.wikipedia.org/w/api.php?format=json&action=query&prop=revisions&rvprop=content&titles=Wisconsin

will return the article for the state of Wisconsin in JSON format is hardly
useful or memorable. The Requests method isn't much better:

.. code:: python

    payload = {'format': 'json', 'action': 'query', 'prop': 'revision', 'rvprop': 'content', 'titles': 'Wisconsin'}
    resp = Requests.get('https://en.wikipedia.org/w/api.php', params=payload).json()

This situation is made worse by the fact that a URL parameter is only
one type of variable. A given API might not only require the developer
to remember (or memorialize in code) that several different variables
exist, but also which of five or more variable types each is.

In Summary
----------

There is a problem with modern REST APIs, and there's no easy solution
available right now. Developers have to write thousands of lines of
boilerplate code that doesn't do anything but re-implement existing
code with slightly different arguments. What's more, because the
developers writing that code aren't the ones who created the API in
the first place, it's easy to make mistakes: mistakes that have to
be fixed by delving into the codebase itself to fix them.

There has to be a better way than this.
