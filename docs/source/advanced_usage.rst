Advanced Usage
==============

beekeeper is designed to be easy-to-use, but its structure also makes it
incredibly adaptable and powerful for advanced users. Right now, there are
three key advanced feature that you may want to take advantage of.

Methods as Variables
--------------------

When initializing a hive, you can pass callable objects like methods and
functions into beekeeper to use as values for variables, as long as there
aren't any variables that need to be used to call them. To avoid this, you
can do a few different things. First, and most easily, they can be object
instance methods. beekeeper will keep those methods linked to their original
contexts, and so their results will be based on the state of their parent
object. You can also use alternate forms of callables, like Python's built-in
"partial" object, which lets you fill in variable values ahead of time.

Either way you do it, you let your beekeeper-generated API move from a simple
static platform to a more robust and dynamic system. Perhaps the most common
use of this feature would be to tie into an OAuth authentication scheme, or some
other system that requires credentials to change automatically over time.

To set this up, just pass in an uncalled method or function as a variable when you
initialize the API. Every time you make an API call, your method will be executed,
and the returned value will be used as the value for that variable.

Custom Data Handlers
--------------------

beekeeper has built-in support for a number of different data types, and
automatically chooses between them based on the defined MIME type of data
being sent, or the Content-Type header of the data being received. Right now,
we can read JSON, plaintext, binary streams, and XML.

But, you might decide that you need something different. For example, you might
want to automatically parse a "text/csv" response into a set of lists, or you might
want to do that the other way around to post "text/csv" data to a server.

First, you'll need to define a data handler class. It should have at least one of
two possible static methods; "dump" and "load". "dump" takes a Python object and
encodes it to a bytes object in the appropriate format; "load" does exactly the
opposite.

You should inherit your class from beekeeper.DataHandler; this will
automatically load it into beekeeper without any further action on your part. To
make sure that it's handling the right data, you'll need to set at least one of
two class variables; `mimetype` or `mimetypes`; `mimetype` should be a single
string with the MIME type you want your class to handle, while if your class
can handle multiple MIME types (as in the case of an XML parser that handles
both 'application/xml' and 'text/xml'), you'll set `mimetypes` to be a list of
those MIME types.

All told, it should look something like this:

.. code:: python

    class CSVHandler(beekeeper.DataHandler):

    mimetype = 'text/csv'

    @staticmethod
    def dump(python_object, encoding):
        """
        Logic goes here - take the Python object the method receives, and parse it
        into a bytes() object. Be sure to use the text encoding passed to the
        "encoding" argument.
        """

    @staticmethod
    def load(response, encoding):
        """
        Again, logic goes here. beekeeper will pass you a bytes() object, as well as the
        encoding the bytes were sent in, and will expect to receive in response a Python
        object that's relevant to the data received.
        """

Because you've informed beekeeper about the specific MIME type that the data handler
should be associated with, beekeeper now knows exactly when to use it: when you define
a data variable that has the defined MIME type of "text/csv", or when a response is
received from the server with "text/csv" in the "Content-Type" header. If a MIME type
doesn't have a data handler associated with it, beekeeper will just return the raw bytes received.

Custom Variable Types
---------------------

Sometimes, you have a variable that's a little particular in its needs, and which you
might want to make a bit easier to use. To do that, you can define a custom variable type
and handler to make things a bit simpler.

For example, when updating contact properties using the Hubspot API, a JSON object in the
following format is required:

.. code:: json

    {
        "properties": [
            {
                "property": "firstname",
                "value": "John"
            },
            {
                "property": "lastname",
                "value": "Smith"
            }
        ]
    }

It's a little bit verbose. And the whole goal of beekeeper is to make your life easier, so
you can put in a little work to make it easier still, just by defining a custom variable
handler and sticking it into beekeeper.

A variable handler takes keyword arguments of the defined type, processes them, and sets
"final variables" of one of the types native to HTTP requests. Those four types are
as follows:

-   "url_param"
-   "header"
-   "url_replacement"
-   "data"

Beekeeper is designed to be able to handle (on a structural level; not necessarily with built-in
code) pretty much any variable type you can throw at it, as long as it can be simplified into those four
variable types. The way it does this is by passing the request object along with the request
to parse a variable; the function that eventually handles the variable can then decide how to
apply the necessary changes to the request.

This is done via four callback methods on the Request object:

-   set_headers(**headers)
-   set_data(data)
-   set_url_params(**params)
-   set_url_replacements(**replacements)

Each of these callback methods can take any number of keyword arguments paired with the final values
for those variables. The exception is the `set_data()` method, which can take a single value, since each
HTTP request can only have a single request body (to get around this, use the multipart variable type).

You can also use the `beekeeper.render_variables` method if your data needs more processing as one of
the built-in types.

Now that we've got some principles down, let's look at our original case. We want a simpler way to write
Hubspot contacts, so let's implement a custom variable type to handle getting them into the right format:

.. code:: python

    @beekeeper.VariableHandler('hs_contact')
    def hubspot_contact_handler(rq, **values):
        #Typically, because this is a data-type object, we only receive one variable.
        for _, contact in values.items():
            x = {
                    'properties': [
                        {'property':prop, 'value': val} for prop, val in contact.items()
                    ]
                }
            beekeeper.render_variables(rq, 'data', data={'value': x, 'mimetype': 'application/json'})

Note the `beekeeper.VariableHandler('hs_contact')` decorator. This decorator wraps up your function
and automatically attaches it to any variable types that you include in the decorator parameters. You
can use a custom variable name, like we did here, or you can bind a custom handler to a built-in
variable type by using its name.

This simple function will perform the transformation we're looking for (we can simply pass in a
dictionary containing the new variable values), and then pass it into the data-rendering pipeline, which
will handle setting both the body data we need, and the appropriate "Content-Type" header. Note that
there isn't a return statement; this is because each function applies its settings directly to the
request.

If you're writing a hive for general distribution, carefully consider the implications of
using custom variable types. Unlike custom data types, beekeeper has no way to handle
hives that use custom variables unless a handler has been bound. Thus, it's best to
create two versions of a hive; one that uses the custom handlers you want, and one that
uses only the standard variable types. You can then use the versioning data in the standard
hive to point to the customized hive in an opt-in manner for consumers who have either
implemented or downloaded an appropriate variable handler.