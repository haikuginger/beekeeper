How does it work?
=================

Variables
---------

One of the big problems with existing REST client solutions is that they
leave it to the developer to track what types of variables need to be put
where. Some of these variable types can be handled automatically, while
others need a bit of coaxing to work right. Beekeeper has the built-in ability
to handle most of the common variable types, as long as the variable is defined
properly within the construct of the Hive file (more details below).

The variable types that beekeeper currently supports are found below:

-   HTTP forms
-   Headers
-   Body data
-   URL string replacements
-   URL parameters
-   HTTP basic authentication
-   HTTP bearer authentication
-   Multipart/form-data
-   Cookies

Data
----

Another item of concern is the way that data going back and forth between
the client and the server is handled. Beekeeper handles this by having a
number of parsers built in; if the data type being sent out matches up
with one of the parsers, beekeeper will use it automatically to dump the
Python object that's passed to it into a stream of bytes. On the way
back, beekeeper reads the response's Content-Type header, and uses the
information it finds there to parse the response back into a Python data
structure; if it can't, it'll simply return the raw bytes to the developer
for further use.

Right now, the MIME types that beekeeper has support for are as follows:

-   application/json
-   application/x-www-form-urlencoded
-   application/octet-stream
-   text/plain
-   text/html
-   application/xml
-   text/xml

Note that any response can be handled in a GZipped format as well; like the
above formats, this encoding is handled automatically by beekeeper.

Note
~~~~

beekeeper uses the third-party xmltodict_ library to handle XML requests
by default. Thus, if you're working with an XML API, be aware of the
usage implications. You can also set a different XML parser by implementing
a custom data handler.

Hive Location
-------------

To be automatically acquired by beekeeper when a developer passes your
domain name (for example, facebook.com) to initialize it, your hive file
must be located as below:

.. code ::

    https://facebook.com/api/hive.json

It is STRONGLY recommended that you server your hive over HTTPS, as it does
change the behavior of client applications. If you serve your hive over HTTP
at this location, then, by default, beekeeper will raise an exception. This
can be suppressed or handled, but it is not ideal.

You can make your hive accessible on any domain you control; it may be easier
to just set up redirects for other domains, though.

Note that subdomains do count as separate domains, so "en.wikipedia.org" would
have its own hive, separate from "wikipedia.org".

Parts of a Hive
---------------

Of course, the primary piece of information that beekeeper uses is the
Hive file format. This is a JSON file with particular elements that tell
beekeeper about the structure of endpoints in the remote API, as well as
how those endpoints relate to the system's native objects and the actions
that can be performed on those objects.

A hive has several elements; we're going to go into detail on each one. By
the time you've read through this section, you should be ready to go out
and start writing your own hive files - or ready to read others and understand
exactly what they mean.

Note that if a key is not described here, it's not currently in use. This means
that, at present, beekeeper won't try to do anything with it, but that's
not a permanent promise in all cases.

name
~~~~

The name of the hive. This is used when printing an API for documentation
purposes.

description
~~~~~~~~~~~

Self-explanatory. Like the name key, it's only used when printing out an
API, and is optional.

root
~~~~

The base URL of the API. All API endpoints should exist under this URL;
sometimes it's as simple as the domain of the website, and sometimes it
can be more complex- for example, an API that might exist on several
different subdomains might have a URL replacement entry in the root
that can be filled out programmatically later on. By convention, the
root URL should not have a closing slash; that should be placed at the
beginning of the endpoint "path" keys lower-down.

mimetype
~~~~~~~~

This key should be a valid MIME type; in general, it should be non-functional,
but it comes into play if we're unable to extract an MIME type from a
server response. It defaults to "application/json".

versioning
~~~~~~~~~~

Example
^^^^^^^

.. code:: json

    {
        "versioning" : {
            "version": 8,
            "previousVersions": [
                "version": 7,
                "location": "http://domain.tld/api/hive_v7.json",
                "expires": "2016-12-31T12:00:00Z"
            ]
        }
    }

The versioning key is completely optional. If you have multiple versions
of your API, or if you iterate your API quickly, then it's good to note the
current version of the API in the "version" subkey, and the details of any
other currently active versions in the "previousVersions" list. An example
of the "versioning" key is provided below.

Each item in the "previousVersions" list contains a version identifier,
as well as a web path to a hive file that can be used to describe that
version of the API. It may also contain an expiry date to indicate that
that version of the API is in the process of deprecation, and will be
shut off after a certain time. Once a version of the API has been deprecated,
it should be removed from the hive file.

If a beekeeper API object is constructed with a version argument, beekeeper
will automatically try to fetch the API version described by parsing the
hive file it receives, determining if it matches the version given, and
if not, loading from the appropriate URL, when available.

variables
~~~~~~~~~

The variables key contains any variables that are universally needed or
used across the entire API, and which are best to fill when the API interface
is constructed. Such variables are passed as arguments during construction,
and will apply to every request thereafter, unless overridden manually.

The variables key is an object mapping variable names to variable objects;
each variable object can have a number of keys, listed below, in order of
how often you'll likely use them:

type
^^^^

This key can bear a number of possible values describing the different kinds of
variables that might be used. Some of them will have special caveats, noted below:

-   **url_param**
    This is the default when a type for the variable is not specified and when a
    custom default variable type is not set on a hive. It appends a query string
    to the URL.
-   **url_replacement**
    No caveats; this simply replaces any "format" blocks in the URL (as denoted by
    curly brackets around a variable name) with the variable's value.
-   **http_basic_auth**
    Handles HTTP basic authorization using a username and password. When doing this,
    we expect to have variables named both "username" and "password"; if either is
    missing, beekeeper behaves as though it's an empty string.
-   **header**
    Sets a header with the given name to the given value.
-   **bearer_token**
    Handles HTTP authorization with a bearer token. The name of this variable is
    not used.
-   **data**
    Sends data in the request body. Only one data-type variable is allowed in
    a given request.
-   **multipart**
    Handles parsing any number of variables into a multipart/form-data request.
-   **cookie**
    Sends a cookie to the server. By default, beekeeper will use cookies within a
    session automatically; it'll pull them from server responses, and send them back
    when needed, without additional definition. Explicitly defining a cookie (which
    is a single string; if you've got a cookie that's a name-pair value, you'll just
    need to pass in "name=value" as the string value) will disable any automatic
    cookie handling for that request and will only send those cookies that are
    explicitly defined.
-   **http_form**
    Sends the key/value pair as part of an application/x-www-form-urlencoded request
    body to the server.

If a variable appears in multiple places, you can alternatively use the "types" key,
which will let you use a list of different variable types; for example, a variable
might need to both be a header and a URL parameter.

If a variable is of two different types in the same "tree", then when executed, it
will act as both types. If it's one type by default higher up (by not having a
specifically defined type), and then it's defined with a different type lower-down
the tree, it'll only have that second type. Finally, if it's defined with one type
higher in the tree, and then defined without an explicit type lower down, the
original high-level type will remain in place without modification.

optional
^^^^^^^^

This is a simple boolean True or False, defaulting to False if the key isn't present.
If "optional" is false, as it is by default, and the variable doesn't receive a value
when it needs to have one, then an exception will be raised, and you'll be prompted
to fill in this variable, as well as any other variables missing values.

Whether a variable is optional is determined by the lowest-level explicit declaration
of such. For example, a variable may be declared as optional for the API as a whole,
but then may be explicitly declared as required on a specific endpoint or action.

value
^^^^^

The value key can be set to anything, as long as it's relevant to the variable type
being used. Typically, though, you'll be using strings. This should typically not
be set inside the hive unless it's being used to control behavior of the API; as
an example, it's OK to set the value of an "action" variable to "login". It is **not**
OK to set the value of a "password" variable to "hunter2".

Values will be filled in at two times; first, when initializing an API interface, and
second, when calling a remote method.

When initializing the API, only variables at the API level will be filled, and will
remain filled throughout the session.

When calling a remote method, variable values are not stored, and are only used in
that specific request.

Values are determined by the most specifc copy of a variable to have a value explicitly
set. From least-specific to most-specific, the levels are API, endpoint, and then action.
A higher-level value may be "un-set" by passing a None value during execution of
a request (after loading the hive into beekeeper) or by setting a lower-level "null"
value within the hive (when writing the JSON file).

mimetype
^^^^^^^^

This key is only used in data-type variables; at present, the "data" type, and the
"multipart" type. It's used to determine what parser to use to translate the data
into binary before transmission, and how to set the Content-Type header. If not
present on "multipart"-type variables, then that specific variable is assumed to
be a standard form field variable, rather than data.

Like the value key, mimetype is determined by the lowest-level explicitly declared
variable.

filename
^^^^^^^^

This key is only used in the "multipart" variable type; because data, in the context
of "multipart" submissions, is assumed to be a file, it may be necessary to set the
name of that virtual file to a specific name. If this filename is not defined within
the hive, then one of two things will happen. If the object passed to the data handler
is a file-like object with a "name" attribute, the value of that attribute will be
used. Otherwise, a random filename in UUID form will be assigned.

Like the value key, filename is determined by the lowest-level explicitly declared
variable.

name
^^^^

Sometimes, it's desirable to have the Python name of a variable be different
from the API name of that variable. In cases like this, you can set the optional
"name" key to have a different string value. If you do so, then within your
programming, you'll address this variable using the name it's keyed by in the
variables object, but external requests will use the value found in this
subkey.

Note that if one of the variables defined in the hive is keyed by a reserved name
in Python, the keyed name will be transferred into the "name" key, and an underscore
will be added to the key used to access that variable within beekeeper. For example,
if a variable is named "from", then to call it, the developer will need to access
it as "_from", but it'll still be sent to the remote server with the appropriate name.
This is also the case for objects and actions with reserved names.

Like the value key, name is determined by the lowest-level explicitly declared
variable.

Example
^^^^^^^

.. code:: json

    {
        "variables": {
            "FileSubmission": {
                "type": "multipart",
                "optional": false,
                "value": {"key1": "val1", "key2": "val2"},
                "mimetype": "application/json",
                "filename": "myupload.json",
                "name": "OtherFileSubmissionName"
            },
            "SimpleDefaultedUrlParam": {
            }
        }
    }

variable_settings
~~~~~~~~~~~~~~~~~

Beekeeper can be configured to have different behaviors around variables. The
variable_settings key can be used to do just that. It's optional, and can contain two
main keys; first, a default_type key that sets what beekeeper is going to do when it
encounters either undefined variables, or a variable with an undefined type. Second,
it can contain a custom_types object that has information about the custom variable
types that the hive uses. If a handler for each of these types isn't present at
initialization of the hive into an API, an exception is raised. Note that the content
of each custom_types key isn't mandated, but it should be descriptive, and ideally
provide the reader with information about how to get or create the handler.

Example
^^^^^^^

.. code:: json

    {
        "variable_settings": {
            "default_type": "url_replacement",
            "custom_types": {
                "special_var": {
                    "description": "Helps with doing cool stuff!",
                    "web_url": "http://mydomain.com/special_var_handler"
                }
            }
        }
    }

endpoints
~~~~~~~~~

The Endpoints key contains definitions of the various different resources available
on the API by distinct URLs. The name of these endpoints isn't hugely important, as
they're not used on a user-facing level. However, they should still have fairly
descriptive names, so that a developer reading your hive file can quickly determine
what's happening.

Each Endpoint object contains four primary keys:

description
^^^^^^^^^^^
This is an optional key that's only used when printing out an API.

path
^^^^

The path key is mandatory; it describes the URL of the endpoint in relation to the
"root" path given at the API level. Like the root, it may contain URL replacement
handlers (variable names within brackets). If you have a number of objects that
use syntactically similar paths, it may be useful to define a URL replacement here
so that you can use the same endpoint for different objects, and avoid writing the
same JSON multiple times.

methods
^^^^^^^

methods is a list of the HTTP methods that may be used on this endpoint. By default,
if no value is given, it is assumed to be a list with a single string "GET". When
executing a request, if the HTTP method that's being used isn't one allowed by this
key, then an exception will be raised.

variables
^^^^^^^^^

variables is an optional key, like at the API level, which contains definitions of variables that are specific to requests on this endpoint. If URL replacements
are being used on this endpoint, it's best to define them here so that appropriate
errors can be raised if they're missing.

Example
^^^^^^^

.. code:: json

    {
        "endpoints": {
            "SingleObjectByID": {
                "path": "/{object_type}/{object_id}",
                "methods": [
                    "GET",
                    "PUT",
                    "DELETE"
                ],
                "variables": {
                    "object_type": {
                        "type": "url_replacement"
                    },
                    "object_id": {
                        "type": "url_replacement"
                    }
                }
            }
        }
    }

objects
~~~~~~~

The Objects key is at the heart of how beekeeper works. Rather than simply handing
the developer a list of endpoints, the Objects key allows beekeeper to define the
relationship between HTTP endpoints and the actual objects that they represent on
the server. It also defines the actions that can be used on those objects.

When an API is initialized in beekeeper, items listed in Objects will be available
as attributes on the parent API object, so names should be chosen carefully, and
should be solely related to the object itself, rather than to the actions that
can be taken with them.

Objects that can be subscripted (more on that later) should
be named plurally so that the idea of them as dictionaries to be opened can be
thought of more naturally. For example, if the name of a single object is "Widget",
the key to that object in the Objects key of the hive should be "Widgets".

As with all objects described so far, any given object will have several keys:

description
^^^^^^^^^^^

This optional key is only used when printing out the API.

id_variable
^^^^^^^^^^^

The id_variable key is a string that defines which variable is filled in when
subscription is used with this object type. If the key is not present, the
object is not subscriptable.

actions
^^^^^^^

The "actions" object contains any number of actions that can be taken based
on the given object. The actions contained therein define the abstraction
between Pythonic object-action pairings and the endpoint-method pairings
used by the remote API.

As with a given object, great thought should go into naming these actions. They
will be used directly by developers when handling your API, so names should be
concise and to the point.

When deciding which Objects to place a given action in, it's best to consider
what object the action is being based off, rather than what type of object
the action ought to return.

For example, if there's an endpoint that gives a list of the Color objects
available with a particular widget, that should exist as the "colors" action
on the "Widgets" object, rather than as the "available_options_by_widget"
action on the Colors object. If in doubt, ask yourself, "what object is the
ID variable I provide this method associated with?"

For fear of repeating myself, as with everything so far, each action has
several subkeys:

description
+++++++++++

This optional key is only used when printing out the API.

endpoint
++++++++

The endpoint key is a string referring to the name of the endpoint that
will be used when the action is called.

method
++++++

The method key is an optional string that defines which HTTP method will 
be used to hit the given endpoint. If no method is given, the action will
default to attempting an HTTP GET.

timeout
+++++++

The optional timeout key is a number that defines the amount of time beekeeper
will wait on data to come from a socket before raising a timeout exception
that you can use to retry the request. The default is five seconds.

variables
+++++++++

The variables key here is identical to the variables object that exists
on the API and Endpoint levels. In practice, of course, you'll use it for
different purposes. For example, if your Action accesses an endpoint that
needs to have variables filled in to make it fit for a particular object,
the best place to do it is here. You may also need to set other parameters
that are specific to the given action.

traverse
++++++++

The Traverse key here lets you define, on a particular action, which parts
of the response data should actually be provided to the program. In some
specific cases, it may be useful to pare down the response to specific
components.

The Traverse key is a list; each item in that list can be either a string or
a list of strings. We start out with the return data in dictionary form, and
proceed recursively through the traversal path. For each item in the path,
we'll do one of several things:

-   If the object we've currently recursed to is a list, we'll return a list
    of each item, each traversed with the remaining elements of the path.

-   If the top item in the path is a list, we'll return a dictionary, with
    one key for each item in the list. The value of each key in the dictionary
    will be the traversed value of the item for that key in the object that
    we're currently recursed to.

-   If the top item in the path is a string with value "*", we'll act similarly
    to what we would do if the top item in the path was a list, but instead of
    looking at just specific keys, we'll return every key in the current object.

-   If the top item in the path is any other string, we'll continue recursively
    navigating through the dictionary entry with that particular key.

In general, if we reach a node where it isn't possible to navigate to the next
path item, we'll raise a TraversalError that contains information about the current
path item as well as the state of the object that we've traversed to. The exception
is if the previous operation was to split a dictionary (as in the case with a
list-type path item, or with a wildcard "*" path item). In this case, if, one of
the objects addressed in such a split is not a normally traversable object (a type
that inherits from either a dictionary or a list), then we'll just return that
object, rather than raising a further exception.

Example
^^^^^^^

.. code:: json

    {
        "Widget": {
            "description": "A widget!",
            "id_variable": "object_id",
            "actions": {
                "get": {
                    "endpoint": "SingleObjectByID",
                    "variables": {
                        "object_type": {
                            "value": "widget"
                        }
                    }
                },
                "update": {
                    "endpoint": "SingleObjectByID",
                    "method": "PUT",
                    "variables": {
                        "object_type": {
                            "value": "widget"
                        },
                        "widget": {
                            "type": "data",
                            "mimetype": "application/json"
                        }
                    }
                },
                "delete": {
                    "endpoint": "SingleObjectByID",
                    "method": "DELETE",
                    "variables": {
                        "object_type": {
                            "value": "widget"
                        }
                    }
                },
                "list": {
                    "endpoint": "ListObjectInstances",
                    "method": "GET",
                    "variables": {
                        "object_type": {
                            "value": "widget"
                        }
                    },
                    "traverse": [
                        "data",
                        "results",
                        "widgets"
                    ]
                }
            }
        }
    }

.. _xmltodict: https://github.com/martinblech/xmltodict